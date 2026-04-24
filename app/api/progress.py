"""
app/api/progress.py
==================
Роутер для прогресса и достижений.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User
from app.models.learning import Block, Lesson, Task, Quiz
from app.models.progress import Achievement, UserAchievement, UserProgress, QuizResult, TaskSubmission
from app.core.security import get_current_user, get_current_user_optional
from app.services.gamification import (
    calculate_level, xp_for_next_level, LEVELS, check_achievements
)
from app.templating import templates

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить общую статистику пользователя.

    Returns:
        ProgressStats с информацией о XP, уровне, прогрессе по блокам и т.д.
    """
    # Получаем данные
    result = await db.execute(select(Lesson))
    total_lessons = len(result.scalars().all())

    result = await db.execute(select(Task))
    total_tasks = len(result.scalars().all())

    result = await db.execute(select(Quiz))
    total_quizzes = len(result.scalars().all())

    # Прогресс по урокам
    result = await db.execute(
        select(func.count(UserProgress.id))
        .where(UserProgress.user_id == current_user.id)
        .where(UserProgress.is_completed == True)
    )
    completed_lessons = result.scalar() or 0

    # Решённые задачи
    result = await db.execute(
        select(func.count(TaskSubmission.id))
        .where(TaskSubmission.user_id == current_user.id)
        .where(TaskSubmission.result == 'PASS')
    )
    solved_tasks = result.scalar() or 0

    # Пройденные квизы
    result = await db.execute(
        select(func.count(QuizResult.id))
        .where(QuizResult.user_id == current_user.id)
        .where(QuizResult.is_passed == True)
    )
    passed_quizzes = result.scalar() or 0

    # Достижения
    result = await db.execute(
        select(func.count(UserAchievement.id))
        .where(UserAchievement.user_id == current_user.id)
    )
    achievements_count = result.scalar() or 0

    # Считаем XP для следующего уровня
    current_level = current_user.level
    if current_level < 10:
        next_level_xp = LEVELS[current_level + 1]
        xp_to_next = next_level_xp - current_user.xp
        xp_in_level = current_user.xp - LEVELS[current_level]
        xp_needed = next_level_xp - LEVELS[current_level]
        xp_progress_percent = int((xp_in_level / xp_needed) * 100) if xp_needed > 0 else 100
    else:
        xp_to_next = 0
        xp_progress_percent = 100

    return {
        'total_xp': current_user.xp,
        'level': current_user.level,
        'xp_to_next_level': max(0, xp_to_next),
        'xp_progress_percent': xp_progress_percent,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'lessons_progress_percent': int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0,
        'total_tasks': total_tasks,
        'solved_tasks': solved_tasks,
        'tasks_progress_percent': int((solved_tasks / total_tasks * 100)) if total_tasks > 0 else 0,
        'total_quizzes': total_quizzes,
        'passed_quizzes': passed_quizzes,
        'quizzes_progress_percent': int((passed_quizzes / total_quizzes * 100)) if total_quizzes > 0 else 0,
        'streak_days': current_user.streak_days,
        'achievements_count': achievements_count,
    }


@router.get("/blocks")
async def get_blocks_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить прогресс по каждому блоку.
    """
    result = await db.execute(
        select(Block).order_by(Block.order_index)
    )
    blocks = result.scalars().all()

    progress_data = []
    for block in blocks:
        # Получаем уроки блока
        result = await db.execute(
            select(Lesson).where(Lesson.block_id == block.id)
        )
        lessons = result.scalars().all()
        lesson_ids = [l.id for l in lessons]

        # Получаем прогресс по урокам
        result = await db.execute(
            select(UserProgress)
            .where(UserProgress.user_id == current_user.id)
            .where(UserProgress.lesson_id.in_(lesson_ids))
            .where(UserProgress.is_completed == True)
        )
        completed = len(result.scalars().all())

        # Считаем XP заработанные в блоке
        result = await db.execute(
            select(TaskSubmission)
            .join(Task)
            .where(TaskSubmission.user_id == current_user.id)
            .where(TaskSubmission.result == 'PASS')
            .where(Task.lesson_id.in_(lesson_ids))
        )
        xp_earned = sum(st.xp_reward or 0 for st in result.scalars().all() if st.xp_reward)

        progress_data.append({
            'block_id': block.id,
            'title': block.title,
            'icon': block.icon,
            'total_lessons': len(lessons),
            'completed_lessons': completed,
            'progress_percent': int((completed / len(lessons) * 100)) if lessons else 0,
            'xp_earned': xp_earned,
        })

    return progress_data


@router.get("/achievements")
async def get_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить все достижения и статус их получения.
    """
    # Получаем все достижения
    result = await db.execute(select(Achievement))
    all_achievements = result.scalars().all()

    # Получаем полученные достижения пользователя
    result = await db.execute(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
    )
    earned_achievements = {ua.achievement_id: ua.earned_at for ua in result.scalars().all()}

    return [
        {
            'id': a.id,
            'code': a.code,
            'title': a.title,
            'description': a.description,
            'icon': a.icon,
            'xp_reward': a.xp_reward,
            'is_earned': a.id in earned_achievements,
            'earned_at': earned_achievements.get(a.id),
        }
        for a in all_achievements
    ]


@router.get("/activity")
async def get_activity_history(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить историю активности за последние N дней.
    """
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=days)

    # Получаем завершённые уроки
    result = await db.execute(
        select(UserProgress)
        .where(UserProgress.user_id == current_user.id)
        .where(UserProgress.is_completed == True)
        .where(UserProgress.completed_at >= start_date)
    )
    lesson_completions = result.scalars().all()

    # Получаем решённые задачи
    result = await db.execute(
        select(TaskSubmission)
        .where(TaskSubmission.user_id == current_user.id)
        .where(TaskSubmission.result == 'PASS')
        .where(TaskSubmission.created_at >= start_date)
    )
    task_solutions = result.scalars().all()

    # Группируем по дням
    activity = {}
    for i in range(days + 1):
        date = start_date + timedelta(days=i)
        activity[date.isoformat()] = {
            'xp_earned': 0,
            'lessons_completed': 0,
            'tasks_solved': 0,
        }

    for lc in lesson_completions:
        date = lc.completed_at.date().isoformat() if lc.completed_at else None
        if date and date in activity:
            activity[date]['lessons_completed'] += 1
            activity[date]['xp_earned'] += 15

    for ts in task_solutions:
        date = ts.created_at.date().isoformat() if ts.created_at else None
        if date and date in activity:
            activity[date]['tasks_solved'] += 1
            activity[date]['xp_earned'] += 30

    return [
        {
            'date': date_str,
            **data,
        }
        for date_str, data in sorted(activity.items())
    ]


@router.get("/dashboard/html")
async def dashboard_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Страница дашборда с прогрессом."""
    # Получаем статистику
    stats = await get_stats(db, current_user)

    # Получаем прогресс по блокам
    blocks_progress = await get_blocks_progress(db, current_user)

    # Получаем достижения
    achievements = await get_achievements(db, current_user)
    earned_count = sum(1 for a in achievements if a['is_earned'])

    # Получаем историю активности
    activity = await get_activity_history(7, db, current_user)

    # Следующая цель
    xp_to_next = stats['xp_to_next_level']
    next_goal = f"До следующего уровня: {xp_to_next} XP"

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
        "stats": stats,
        "blocks_progress": blocks_progress,
        "achievements": achievements[:5],  # Только первые 5
        "earned_count": earned_count,
        "activity": activity,
        "next_goal": next_goal,
    })