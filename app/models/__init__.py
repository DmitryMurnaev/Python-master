"""
app/models/__init__.py
====================
Модели базы данных.

Импортируем все модели для удобства работы с Alembic и создания таблиц.
"""

from app.db.session import Base
from app.models.user import User
from app.models.learning import Block, Lesson, Quiz, Task
from app.models.progress import (
    UserProgress,
    QuizResult,
    TaskSubmission,
    Achievement,
    UserAchievement,
)
from app.models.flashcard import FlashCard, DailyChallenge

__all__ = [
    "Base",
    "User",
    "Block",
    "Lesson",
    "Quiz",
    "Task",
    "UserProgress",
    "QuizResult",
    "TaskSubmission",
    "Achievement",
    "UserAchievement",
    "FlashCard",
    "DailyChallenge",
]