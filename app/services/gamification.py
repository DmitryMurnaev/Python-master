"""
app/services/gamification.py
===========================
Сервис геймификации - XP, уровни, достижения, streak.

Этот модуль инкапсулирует всю логику прогрессирования,
чтобы не засорять бизнес-логику роутеров.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.progress import Achievement, UserAchievement, TaskSubmission, QuizResult
from app.models.learning import Block, Lesson, Task, Quiz
from app.models.flashcard import DailyChallenge


# Конфигурация уровней
# Каждый уровень требует всё больше XP
LEVELS = {
    1: 0,       # Start
    2: 100,     # 100 XP
    3: 250,     # +150 XP
    4: 450,     # +200 XP
    5: 700,     # +250 XP
    6: 1000,    # +300 XP
    7: 1350,    # +350 XP
    8: 1750,    # +400 XP
    9: 2200,    # +450 XP
    10: 2700,   # +500 XP - Max level
}

# XP награды за действия
XP_REWARDS = {
    'quiz_correct': 10,      # Правильный ответ в квизе
    'task_solved': 30,       # Решённая задача
    'block_completed': 50,   # Завершённый блок
    'lesson_completed': 15,  # Завершённый урок
    'daily_challenge': 20,   # Ежедневный челлендж
    'achievement': 25,       # Полученное достижение
    'streak_bonus': 10,      # Бонус за streak
}


def calculate_level(xp: int) -> int:
    """
    Вычисляет уровень по количеству XP.

    Args:
        xp: Количество очков опыта

    Returns:
        Уровень (1-10)
    """
    level = 1
    for lvl, required_xp in sorted(LEVELS.items(), reverse=True):
        if xp >= required_xp:
            level = lvl
            break
    return level


def xp_for_next_level(current_xp: int) -> tuple[int, int]:
    """
    Возвращает XP для следующего уровня и прогресс до него.

    Args:
        current_xp: Текущее количество XP

    Returns:
        (xp_to_next, xp_in_level)
    """
    current_level = calculate_level(current_xp)

    if current_level >= 10:
        return 0, 0  # Максимальный уровень

    next_level_xp = LEVELS[current_level + 1]
    current_level_xp = LEVELS[current_level]

    xp_to_next = next_level_xp - current_xp
    xp_in_level = current_xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp

    return xp_to_next, xp_in_level, xp_needed


async def update_user_xp(
    db: AsyncSession,
    user: User,
    amount: int,
    reason: str = None
) -> User:
    """
    Добавляет XP пользователю и обновляет уровень при необходимости.

    Args:
        db: Сессия БД
        user: Пользователь
        amount: Количество XP для добавления
        reason: Причина (для логирования)

    Returns:
        Обновлённый пользователь
    """
    user.xp += amount

    # Проверяем повышение уровня
    new_level = calculate_level(user.xp)
    if new_level > user.level:
        user.level = new_level
        # Можно добавить уведомление о повышении уровня

    await db.commit()
    await db.refresh(user)

    return user


async def update_streak(db: AsyncSession, user: User) -> User:
    """
    Обновляет streak пользователя.

    Args:
        db: Сессия БД
        user: Пользователь

    Returns:
        Обновлённый пользователь
    """
    today = datetime.now(timezone.utc).date()
    last_activity = user.last_activity_date

    if last_activity:
        last_date = last_activity.date() if isinstance(last_activity, datetime) else last_activity

        if last_date == today:
            # Уже активен сегодня
            pass
        elif (today - last_date).days == 1:
            # Вчера был активен - увеличиваем streak
            user.streak_days += 1
        else:
            # Streak сломан - начинаем сначала
            user.streak_days = 1
    else:
        # Первый день
        user.streak_days = 1

    user.last_activity_date = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    return user


# Предопределённые достижения
ACHIEVEMENTS_DATA = [
    {
        'code': 'first_code',
        'title': 'Первый код',
        'description': 'Запустите свою первую программу',
        'icon': '🐍',
        'xp_reward': 10,
    },
    {
        'code': 'variables_master',
        'title': 'Массивовед',
        'description': 'Правильно используйте переменные и типы данных',
        'icon': '📊',
        'xp_reward': 20,
    },
    {
        'code': 'loop_wizard',
        'title': 'Мастер циклов',
        'description': 'Используйте циклы for и while',
        'icon': '🔄',
        'xp_reward': 20,
    },
    {
        'code': 'function_master',
        'title': 'Функционёр',
        'description': 'Создайте и используйте функции',
        'icon': '⚙️',
        'xp_reward': 20,
    },
    {
        'code': 'oop_master',
        'title': 'ООП-мастер',
        'description': 'Освойте объектно-ориентированное программирование',
        'icon': '🏗️',
        'xp_reward': 30,
    },
    {
        'code': 'task_solver_10',
        'title': 'Решатель задач',
        'description': 'Решите 10 задач',
        'icon': '🧩',
        'xp_reward': 25,
    },
    {
        'code': 'task_solver_50',
        'title': 'Мастер задач',
        'description': 'Решите 50 задач',
        'icon': '🧩',
        'xp_reward': 50,
    },
    {
        'code': 'quiz_perfect',
        'title': 'Идеальный квиз',
        'description': 'Пройдите квиз со 100% правильных ответов',
        'icon': '💯',
        'xp_reward': 20,
    },
    {
        'code': 'streak_3',
        'title': 'Три дня подряд',
        'description': 'Занимайтесь 3 дня подряд',
        'icon': '🔥',
        'xp_reward': 15,
    },
    {
        'code': 'streak_7',
        'title': 'Недельный огонь',
        'description': 'Занимайтесь 7 дней подряд',
        'icon': '🔥',
        'xp_reward': 30,
    },
    {
        'code': 'streak_30',
        'title': 'Месяц каждый день',
        'description': 'Занимайтесь 30 дней подряд',
        'icon': '🔥',
        'xp_reward': 100,
    },
    {
        'code': 'block_finished',
        'title': 'Первый блок',
        'description': 'Завершите первый блок обучения',
        'icon': '📚',
        'xp_reward': 30,
    },
    {
        'code': 'all_blocks',
        'title': 'Python Мастер',
        'description': 'Пройдите все блоки',
        'icon': '🏆',
        'xp_reward': 200,
    },
    {
        'code': 'cards_50',
        'title': 'Карточный мастер',
        'description': 'Создайте 50 карточек',
        'icon': '🃏',
        'xp_reward': 20,
    },
    {
        'code': 'cards_reviewed_100',
        'title': 'Повторяющий',
        'description': 'Повторите 100 карточек',
        'icon': '📖',
        'xp_reward': 20,
    },
]


async def check_achievements(db: AsyncSession, user: User) -> list[Achievement]:
    """
    Проверяет и выдаёт достижения пользователю.

    Args:
        db: Сессия БД
        user: Пользователь

    Returns:
        Список новых полученных достижений
    """
    new_achievements = []

    # Получаем все достижения пользователя
    result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    )
    earned_ids = {row[0] for row in result.fetchall()}

    # Получаем все достижения
    result = await db.execute(select(Achievement))
    all_achievements = result.scalars().all()

    for achievement in all_achievements:
        if achievement.id in earned_ids:
            continue  # Уже получено

        earned = False

        # Проверяем критерии каждого достижения
        if achievement.code == 'first_code':
            # Просто наличие любого решения
            result = await db.execute(
                select(TaskSubmission).where(TaskSubmission.user_id == user.id).limit(1)
            )
            if result.scalar_one_or_none():
                earned = True

        elif achievement.code == 'task_solver_10':
            count = await db.execute(
                select(func.count(TaskSubmission.id))
                .where(TaskSubmission.user_id == user.id)
                .where(TaskSubmission.result == 'PASS')
            )
            if count.scalar() >= 10:
                earned = True

        elif achievement.code in ('streak_3', 'streak_7', 'streak_30'):
            streak_map = {'streak_3': 3, 'streak_7': 7, 'streak_30': 30}
            if user.streak_days >= streak_map[achievement.code]:
                earned = True

        elif achievement.code == 'quiz_perfect':
            result = await db.execute(
                select(QuizResult).where(QuizResult.user_id == user.id).where(QuizResult.score == 100.0).limit(1)
            )
            if result.scalar_one_or_none():
                earned = True

        if earned:
            # Добавляем достижение
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                earned_at=datetime.now(timezone.utc)
            )
            db.add(user_achievement)
            new_achievements.append(achievement)

    if new_achievements:
        await db.commit()

    return new_achievements


async def create_default_achievements(db: AsyncSession):
    """
    Создаёт предопределённые достижения в базе данных.

    Вызывается при инициализации БД.
    """
    for data in ACHIEVEMENTS_DATA:
        # Проверяем что достижение ещё не существует
        result = await db.execute(
            select(Achievement).where(Achievement.code == data['code'])
        )
        if result.scalar_one_or_none():
            continue

        achievement = Achievement(**data)
        db.add(achievement)

    await db.commit()