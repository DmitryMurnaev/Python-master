"""
app/api/flashcards.py
=====================
Роутер для карточек - CRUD и интервальное повторение.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User
from app.models.learning import Block
from app.models.flashcard import FlashCard, DailyChallenge
from app.core.security import get_current_user
from app.schemas.flashcard import (
    FlashCardCreate, FlashCardUpdate, FlashCardResponse,
    FlashCardReview, FlashCardStudySession, FlashCardStats
)
from app.services.gamification import update_user_xp, XP_REWARDS

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.get("/")
async def get_flashcards(
    block_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить все карточки пользователя.

    Args:
        block_id: Фильтр по блоку (опционально)
    """
    query = select(FlashCard).where(FlashCard.user_id == current_user.id)

    if block_id:
        query = query.where(FlashCard.block_id == block_id)

    result = await db.execute(query.order_by(FlashCard.next_review_date))
    cards = result.scalars().all()

    return [
        {
            'id': card.id,
            'question': card.question,
            'answer': card.answer,
            'block_id': card.block_id,
            'interval': card.interval,
            'ease_factor': card.ease_factor,
            'repetitions': card.repetitions,
            'next_review_date': card.next_review_date,
            'is_due': card.next_review_date <= datetime.now(timezone.utc).replace(tzinfo=None),
        }
        for card in cards
    ]


@router.post("/")
async def create_flashcard(
    card: FlashCardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новую карточку.

    Args:
        card: Данные карточки
    """
    flashcard = FlashCard(
        user_id=current_user.id,
        question=card.question,
        answer=card.answer,
        block_id=card.block_id,
        next_review_date=datetime.now(timezone.utc).replace(tzinfo=None),  # Показываем сразу
    )
    db.add(flashcard)
    await db.commit()
    await db.refresh(flashcard)

    return {
        'id': flashcard.id,
        'message': 'Карточка создана',
    }


@router.put("/{card_id}")
async def update_flashcard(
    card_id: int,
    card_update: FlashCardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить карточку.

    Args:
        card_id: ID карточки
        card_update: Новые данные
    """
    result = await db.execute(
        select(FlashCard)
        .where(FlashCard.id == card_id)
        .where(FlashCard.user_id == current_user.id)
    )
    flashcard = result.scalar_one_or_none()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    if card_update.question is not None:
        flashcard.question = card_update.question
    if card_update.answer is not None:
        flashcard.answer = card_update.answer
    if card_update.block_id is not None:
        flashcard.block_id = card_update.block_id

    await db.commit()

    return {'message': 'Карточка обновлена'}


@router.delete("/{card_id}")
async def delete_flashcard(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить карточку.

    Args:
        card_id: ID карточки
    """
    result = await db.execute(
        select(FlashCard)
        .where(FlashCard.id == card_id)
        .where(FlashCard.user_id == current_user.id)
    )
    flashcard = result.scalar_one_or_none()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    await db.delete(flashcard)
    await db.commit()

    return {'message': 'Карточка удалена'}


@router.get("/study")
async def get_study_session(
    limit: int = 20,
    block_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить карточки для изучения (которые нужно повторить).

    Использует алгоритм SM-2 для выбора карточек.

    Args:
        limit: Максимальное количество карточек
        block_id: Фильтр по блоку
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    query = select(FlashCard).where(
        FlashCard.user_id == current_user.id,
        FlashCard.next_review_date <= now
    )

    if block_id:
        query = query.where(FlashCard.block_id == block_id)

    result = await db.execute(query.order_by(FlashCard.next_review_date).limit(limit))
    cards = result.scalars().all()

    return FlashCardStudySession(
        cards=[
            FlashCardResponse(
                id=card.id,
                user_id=card.user_id,
                question=card.question,
                answer=card.answer,
                block_id=card.block_id,
                interval=card.interval,
                ease_factor=card.ease_factor,
                repetitions=card.repetitions,
                next_review_date=card.next_review_date,
                is_due=True,
            )
            for card in cards
        ],
        total_cards=len(cards),
        due_cards=len(cards),
    )


@router.post("/review")
async def review_card(
    review: FlashCardReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Оценить карточку после просмотра.

    Использует алгоритм SM-2 для обновления интервала.

    Args:
        review: ID карточки и качество ответа (0-5)
    """
    result = await db.execute(
        select(FlashCard)
        .where(FlashCard.id == review.card_id)
        .where(FlashCard.user_id == current_user.id)
    )
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    # Обновляем карточку по алгоритму SM-2
    card.update_sm2(review.quality)
    await db.commit()

    return {
        'message': 'Карточка обновлена',
        'next_review': card.next_review_date,
        'interval': card.interval,
    }


@router.get("/stats")
async def get_flashcard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить статистику карточек.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Всего карточек
    result = await db.execute(
        select(func.count(FlashCard.id))
        .where(FlashCard.user_id == current_user.id)
    )
    total = result.scalar() or 0

    # Карточек на повторение сегодня
    result = await db.execute(
        select(func.count(FlashCard.id))
        .where(FlashCard.user_id == current_user.id)
        .where(FlashCard.next_review_date <= now)
    )
    due = result.scalar() or 0

    # В процессе обучения (interval < 21)
    result = await db.execute(
        select(func.count(FlashCard.id))
        .where(FlashCard.user_id == current_user.id)
        .where(FlashCard.interval < 21)
        .where(FlashCard.interval > 1)
    )
    learning = result.scalar() or 0

    # Освоено (interval >= 21)
    result = await db.execute(
        select(func.count(FlashCard.id))
        .where(FlashCard.user_id == current_user.id)
        .where(FlashCard.interval >= 21)
    )
    mastered = result.scalar() or 0

    return FlashCardStats(
        total_cards=total,
        cards_due_today=due,
        cards_learning=learning,
        cards_mastered=mastered,
        reviews_today=0,  # Можно считать из DailyChallenge
    )


@router.get("/daily")
async def get_daily_challenge(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить ежедневный челлендж.
    """
    today = datetime.now(timezone.utc).date()

    # Ищем челлендж на сегодня
    result = await db.execute(
        select(DailyChallenge)
        .where(DailyChallenge.user_id == current_user.id)
        .where(
            func.date(DailyChallenge.date) == today
        )
    )
    challenge = result.scalar_one_or_none()

    if not challenge:
        # Создаём новый челлендж - случайная задача из пройденных
        from app.models.learning import Task
        from sqlalchemy import func as sql_func

        # Берём случайную задачу из любого блока
        result = await db.execute(
            select(Task).order_by(sql_func.random()).limit(1)
        )
        task = result.scalar_one_or_none()

        if task:
            challenge = DailyChallenge(
                user_id=current_user.id,
                task_id=task.id,
                date=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.add(challenge)
            await db.commit()
            await db.refresh(challenge)

    if challenge:
        return {
            'id': challenge.id,
            'task_id': challenge.task_id,
            'task_title': challenge.task.title if challenge.task else 'Unknown',
            'date': challenge.date,
            'is_completed': challenge.is_completed,
            'is_rewarded': challenge.is_rewarded,
            'xp_reward': 20,
        }

    return None


@router.post("/daily/{challenge_id}/complete")
async def complete_daily_challenge(
    challenge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отметить ежедневный челлендж выполненным.
    """
    result = await db.execute(
        select(DailyChallenge)
        .where(DailyChallenge.id == challenge_id)
        .where(DailyChallenge.user_id == current_user.id)
    )
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(status_code=404, detail="Челлендж не найден")

    if challenge.is_completed:
        return {'message': 'Челлендж уже выполнен', 'xp_earned': 0}

    challenge.is_completed = True

    # Начисляем XP
    xp_reward = 20
    await update_user_xp(db, current_user, xp_reward, "Ежедневный челлендж")
    challenge.is_rewarded = True

    await db.commit()

    return {'message': 'Челлендж выполнен', 'xp_earned': xp_reward}