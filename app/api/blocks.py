"""
app/api/blocks.py
=================
Роутер для блоков и уроков - навигация по курсу.

Этот роутер отвечает за:
1. Список всех блоков с прогрессом
2. Детали блока с уроками
3. Страница урока с теорией
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.learning import Block, Lesson, Quiz, Task
from app.models.progress import UserProgress, QuizResult, TaskSubmission
from app.core.security import get_current_user, get_current_user_optional
from app.schemas.learning import (
    BlockResponse, BlockDetail, LessonResponse, LessonDetail,
    TaskResponse, QuizResponse
)
from app.templating import render

router = APIRouter(prefix="/api/blocks", tags=["blocks"])


@router.get("/")
async def get_blocks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Получить список всех блоков с прогрессом пользователя.

    Args:
        db: Сессия БД
        current_user: Текущий пользователь (опционально)

    Returns:
        Список BlockResponse с информацией о прогрессе
    """
    # Получаем все блоки отсортированные по order_index
    result = await db.execute(
        select(Block).order_by(Block.order_index)
    )
    blocks = result.scalars().all()

    # Получаем прогресс пользователя если он авторизован
    user_progress = {}
    if current_user:
        result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == current_user.id)
        )
        for progress in result.scalars().all():
            user_progress[progress.lesson_id] = progress.is_completed

    # Формируем ответ
    blocks_data = []
    for block in blocks:
        # Считаем уроки в блоке
        result = await db.execute(
            select(func.count(Lesson.id)).where(Lesson.block_id == block.id)
        )
        lessons_count = result.scalar() or 0

        # Считаем пройденные уроки
        result = await db.execute(
            select(Lesson.id).where(Lesson.block_id == block.id)
        )
        lesson_ids = [row[0] for row in result.fetchall()]
        completed_count = sum(1 for lid in lesson_ids if user_progress.get(lid))

        # Считаем прогресс в процентах
        progress_percent = int((completed_count / lessons_count * 100)) if lessons_count > 0 else 0

        blocks_data.append(BlockResponse(
            id=block.id,
            title=block.title,
            description=block.description,
            icon=block.icon,
            min_level=block.min_level,
            xp_reward=block.xp_reward,
            order_index=block.order_index,
            lessons_count=lessons_count,
            completed_lessons=completed_count,
            progress_percent=progress_percent,
        ))

    return blocks_data


@router.get("/{block_id}")
async def get_block_detail(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Получить детали блока с уроками.

    Args:
        block_id: ID блока
        db: Сессия БД
        current_user: Текущий пользователь
    """
    # Получаем блок
    result = await db.execute(select(Block).where(Block.id == block_id))
    block = result.scalar_one_or_none()

    if not block:
        raise HTTPException(status_code=404, detail="Блок не найден")

    # Проверяем уровень доступа
    if current_user and current_user.level < block.min_level:
        raise HTTPException(
            status_code=403,
            detail=f"Для доступа к этому блоку нужен уровень {block.min_level}"
        )

    # Получаем уроки блока
    result = await db.execute(
        select(Lesson)
        .where(Lesson.block_id == block_id)
        .options(
            selectinload(Lesson.quizzes),
            selectinload(Lesson.tasks)
        )
        .order_by(Lesson.order_index)
    )
    lessons = result.scalars().all()

    # Получаем прогресс пользователя
    user_progress = {}
    if current_user:
        result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == current_user.id)
        )
        for progress in result.scalars().all():
            user_progress[progress.lesson_id] = progress.is_completed

    # Получаем решённые задачи
    solved_tasks = set()
    if current_user:
        result = await db.execute(
            select(TaskSubmission.task_id)
            .where(TaskSubmission.user_id == current_user.id)
            .where(TaskSubmission.result == 'PASS')
        )
        solved_tasks = {row[0] for row in result.fetchall()}

    # Формируем данные уроков
    lessons_data = []
    prev_completed = True  # Первый урок не заблокирован

    for lesson in lessons:
        is_completed = user_progress.get(lesson.id, False)
        is_locked = not prev_completed  # Блокируем пока предыдущий не пройден

        lessons_data.append(LessonDetail(
            id=lesson.id,
            block_id=lesson.block_id,
            order_index=lesson.order_index,
            title=lesson.title,
            description=lesson.description,
            content=lesson.content,
            is_project=lesson.is_project,
            xp_reward=lesson.xp_reward,
            is_completed=is_completed,
            is_locked=is_locked,
            quizzes_count=len(lesson.quizzes),
            tasks_count=len(lesson.tasks),
            quizzes=[
                QuizResponse(
                    id=q.id,
                    lesson_id=q.lesson_id,
                    title=q.title,
                    passing_score=q.passing_score,
                    questions_count=len(eval(q.questions)) if q.questions else 0,
                )
                for q in lesson.quizzes
            ],
            tasks=[
                TaskResponse(
                    id=t.id,
                    lesson_id=t.lesson_id,
                    order_index=t.order_index,
                    title=t.title,
                    description=t.description,
                    starter_code=t.starter_code,
                    hints=t.hints,
                    xp_reward=t.xp_reward,
                    is_solved=t.id in solved_tasks,
                    attempts_count=0,  # Можно добавить подсчёт
                )
                for t in lesson.tasks
            ],
        ))

        prev_completed = is_completed or is_locked

    return BlockDetail(
        id=block.id,
        title=block.title,
        description=block.description,
        icon=block.icon,
        min_level=block.min_level,
        xp_reward=block.xp_reward,
        order_index=block.order_index,
        lessons_count=len(lessons),
        completed_lessons=sum(1 for l in lessons_data if l.is_completed),
        progress_percent=int(sum(1 for l in lessons_data if l.is_completed) / len(lessons) * 100) if lessons else 0,
        lessons=lessons_data,
    )


@router.get("/{block_id}/html")
async def get_block_page(
    block_id: int,
    request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Возвращает HTML страницу блока."""
    block_detail = await get_block_detail(block_id, db, current_user)
    return render("blocks/block_detail.html", {
        "request": request,
        "block": block_detail,
        "user": current_user,
    })


@router.get("/lesson/{lesson_id}")
async def get_lesson_page(
    lesson_id: int,
    request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Страница урока с теорией и задачами.

    Args:
        lesson_id: ID урока
    """
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.quizzes),
            selectinload(Lesson.tasks),
            selectinload(Lesson.block)
        )
    )
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Получаем прогресс пользователя
    is_completed = False
    if current_user:
        result = await db.execute(
            select(UserProgress)
            .where(UserProgress.user_id == current_user.id)
            .where(UserProgress.lesson_id == lesson_id)
        )
        progress = result.scalar_one_or_none()
        if progress:
            is_completed = progress.is_completed

    # Получаем решённые задачи
    solved_tasks = {}
    if current_user:
        result = await db.execute(
            select(TaskSubmission)
            .where(TaskSubmission.user_id == current_user.id)
            .where(TaskSubmission.result == 'PASS')
        )
        for sub in result.scalars().all():
            solved_tasks[sub.task_id] = True

    # Формируем данные
    quizzes_data = [
        {
            'id': q.id,
            'title': q.title,
            'questions': eval(q.questions) if q.questions else [],
            'passing_score': q.passing_score,
        }
        for q in lesson.quizzes
    ]

    tasks_data = [
        {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'starter_code': t.starter_code or '',
            'hints': t.hints_list if hasattr(t, 'hints_list') else [],
            'expected_output': t.expected_output,
            'is_solved': solved_tasks.get(t.id, False),
            'xp_reward': t.xp_reward,
        }
        for t in lesson.tasks
    ]

    return render("lessons/lesson_page.html", {
        "request": request,
        "lesson": lesson,
        "quizzes": quizzes_data,
        "tasks": tasks_data,
        "is_completed": is_completed,
        "user": current_user,
    })


@router.post("/lesson/{lesson_id}/complete")
async def mark_lesson_complete(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отметить урок как пройденный.

    Args:
        lesson_id: ID урока
        current_user: Текущий пользователь
    """
    from datetime import datetime, timezone

    # Проверяем что урок существует
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем или создаём прогресс
    result = await db.execute(
        select(UserProgress)
        .where(UserProgress.user_id == current_user.id)
        .where(UserProgress.lesson_id == lesson_id)
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
        )
        db.add(progress)

    progress.is_completed = True
    progress.completed_at = datetime.now(timezone.utc)

    await db.commit()

    # Добавляем XP за урок
    from app.services.gamification import update_user_xp, XP_REWARDS
    await update_user_xp(db, current_user, XP_REWARDS['lesson_completed'], "Завершение урока")

    return {"message": "Урок отмечен как пройденный", "xp_earned": XP_REWARDS['lesson_completed']}