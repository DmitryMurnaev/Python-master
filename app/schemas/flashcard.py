"""
app/schemas/flashcard.py
=======================
Pydantic схемы для карточек (flashcards).
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class FlashCardBase(BaseModel):
    """Базовая схема карточки."""
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    block_id: Optional[int] = None


class FlashCardCreate(FlashCardBase):
    """Схема для создания карточки."""
    pass


class FlashCardUpdate(BaseModel):
    """Схема для обновления карточки."""
    question: Optional[str] = Field(None, min_length=1)
    answer: Optional[str] = Field(None, min_length=1)
    block_id: Optional[int] = None


class FlashCardResponse(FlashCardBase):
    """Ответ с данными карточки."""
    id: int
    user_id: int
    interval: int
    ease_factor: float
    repetitions: int
    next_review_date: datetime
    is_due: bool = False  # Нужно ли повторить сегодня

    model_config = {"from_attributes": True}


class FlashCardReview(BaseModel):
    """Отзыв после просмотра карточки."""
    card_id: int
    quality: int = Field(..., ge=0, le=5, description="Качество ответа 0-5")


class FlashCardStudySession(BaseModel):
    """Сесия изучения карточек."""
    cards: list[FlashCardResponse]
    total_cards: int
    due_cards: int


class FlashCardStats(BaseModel):
    """Статистика карточек пользователя."""
    total_cards: int = 0
    cards_due_today: int = 0
    cards_learning: int = 0
    cards_mastered: int = 0  # interval > 21 день
    reviews_today: int = 0