"""
app/api/quiz.py
===============
Роутер для квизов - проверка ответов, подсчёт результатов.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.learning import Quiz, Lesson
from app.models.progress import QuizResult, UserProgress
from app.core.security import get_current_user
from app.schemas.learning import QuizSubmission, QuizResultResponse
from app.services.gamification import update_user_xp, XP_REWARDS, check_achievements

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить квиз с вопросами.

    Args:
        quiz_id: ID квиза
    """
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Парсим вопросы из JSON
    questions = json.loads(quiz.questions) if quiz.questions else []

    return {
        'id': quiz.id,
        'title': quiz.title,
        'lesson_id': quiz.lesson_id,
        'questions': questions,
        'passing_score': quiz.passing_score,
    }


@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    submission: QuizSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Проверить ответы квиза и сохранить результат.

    Args:
        quiz_id: ID квиза
        submission: Ответы пользователя
    """
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Парсим вопросы
    questions = json.loads(quiz.questions) if quiz.questions else []

    if len(submission.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Ожидается {len(questions)} ответов, получено {len(submission.answers)}"
        )

    # Подсчитываем правильные ответы
    correct_count = 0
    for i, (answer, question) in enumerate(zip(submission.answers, questions)):
        if answer == question['correct']:
            correct_count += 1

    # Вычисляем процент
    score = (correct_count / len(questions)) * 100 if questions else 0
    is_passed = score >= quiz.passing_score

    # Сохраняем результат
    quiz_result = QuizResult(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        correct_answers=correct_count,
        total_questions=len(questions),
        is_passed=is_passed,
    )
    db.add(quiz_result)

    # Обновляем прогресс по уроку
    result = await db.execute(
        select(UserProgress)
        .where(UserProgress.user_id == current_user.id)
        .where(UserProgress.lesson_id == quiz.lesson_id)
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=quiz.lesson_id,
        )
        db.add(progress)

    # Считаем что урок пройден если квиз пройден успешно
    if is_passed and not progress.is_completed:
        from datetime import datetime, timezone
        progress.is_completed = True
        progress.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.commit()

    # Начисляем XP за правильные ответы
    xp_earned = 0
    if is_passed:
        xp_earned = correct_count * XP_REWARDS['quiz_correct']
        await update_user_xp(db, current_user, xp_earned, "Прохождение квиза")

    # Проверяем достижения
    new_achievements = await check_achievements(db, current_user)

    return QuizResultResponse(
        score=score,
        correct_answers=correct_count,
        total_questions=len(questions),
        is_passed=is_passed,
        xp_earned=xp_earned,
    )


@router.get("/{quiz_id}/history")
async def get_quiz_history(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить историю прохождения квиза.

    Args:
        quiz_id: ID квиза
    """
    result = await db.execute(
        select(QuizResult)
        .where(QuizResult.user_id == current_user.id)
        .where(QuizResult.quiz_id == quiz_id)
        .order_by(QuizResult.created_at.desc())
    )
    history = result.scalars().all()

    return [
        {
            'id': r.id,
            'score': r.score,
            'correct_answers': r.correct_answers,
            'total_questions': r.total_questions,
            'is_passed': r.is_passed,
            'created_at': r.created_at,
        }
        for r in history
    ]