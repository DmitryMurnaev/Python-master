"""
app/models/user.py
=================
Модель пользователя.

Поля:
- id: Уникальный идентификатор
- username: Имя пользователя (уникальное)
- email: Email (уникальный)
- hashed_password: Хешированный пароль
- is_active: Активен ли аккаунт
- created_at: Дата регистрации
- xp: Очки опыта (experience points)
- level: Текущий уровень (1-10)
- streak_days: Количество дней подряд
- last_activity_date: Дата последней активности
- theme: Тема оформления (dark/light)
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.session import Base


class User(Base):
    """
    Модель пользователя системы.

    Используем современный стиль SQLAlchemy 2.0 с mapped_column().
    Вместо username используем email как основной идентификатор для входа.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Gamification поля
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    theme: Mapped[str] = mapped_column(String(10), default="dark")

    # Связи с другими таблицами
    # back_populates указывает на обратную сторону отношения
    progress: Mapped[list["UserProgress"]] = relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan"
    )
    quiz_results: Mapped[list["QuizResult"]] = relationship(
        "QuizResult", back_populates="user", cascade="all, delete-orphan"
    )
    task_submissions: Mapped[list["TaskSubmission"]] = relationship(
        "TaskSubmission", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )
    flashcards: Mapped[list["FlashCard"]] = relationship(
        "FlashCard", back_populates="user", cascade="all, delete-orphan"
    )
    daily_challenges: Mapped[list["DailyChallenge"]] = relationship(
        "DailyChallenge", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, level={self.level})>"