"""
app/models/flashcard.py
======================
Модель карточек для интервального повторения (как Anki).

Структура:
- FlashCard: Карточка с вопросом и ответом
- Две стороны: question (передняя) и answer (задняя)
- Система интервального повторения: next_review_date, interval, ease_factor

Алгоритм интервального повторения (SM-2):
- ease_factor: множитель интервала (стартует с 2.5)
- interval: дней до следующего повтора
- Если ответ правильный: увеличиваем интервал
- Если неправильный: сбрасываем интервал
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.session import Base


class FlashCard(Base):
    """
    Карточка для изучения.

    Поля:
    - question: Текст вопроса (передняя сторона)
    - answer: Ответ (задняя сторона)
    - block_id: К какому блоку относится (для фильтрации)
    - interval: Текущий интервал в днях
    - ease_factor: Множитель интервала (2.5 по умолчанию)
    - repetitions: Количество успешных повторений подряд
    - next_review_date: Когда показать карточку снова
    """
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    block_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("blocks.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    # SM-2 алгоритм
    interval: Mapped[int] = mapped_column(Integer, default=1)  # дней
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_reviewed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="flashcards")
    block: Mapped[Optional["Block"]] = relationship("Block")

    def update_sm2(self, quality: int):
        """
        Обновляет карточку после ответа по алгоритму SM-2.

        Args:
            quality: Качество ответа (0-5)
                0 - полностью забыл
                1 - неверный ответ, но вспомнил при подсказке
                2 - верный ответ с трудом
                3 - верный ответ
                4 - верный ответ легко
                5 - слишком просто

        Интервал растёт так: 1 -> 6 -> interval * ease_factor
        """
        if quality < 3:
            # Неправильный ответ - начинаем сначала
            self.repetitions = 0
            self.interval = 1
        else:
            # Правильный ответ
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)

            self.repetitions += 1

        # Обновляем ease_factor
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        self.ease_factor = max(
            1.3,
            self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )

        # Устанавливаем дату следующего повтора
        self.next_review_date = datetime.now(timezone.utc) + timedelta(days=self.interval)
        self.last_reviewed = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<FlashCard(id={self.id}, question={self.question[:30]}...)>"


class DailyChallenge(Base):
    """
    Ежедневный челлендж - случайная задача для повторения.

    Каждый день пользователь получает одну задачу на повторение.
    Это мотивирует заходить каждый день и поддерживать навыки.
    """
    __tablename__ = "daily_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_rewarded: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="daily_challenges")
    task: Mapped["Task"] = relationship("Task")

    @classmethod
    def get_today_key(cls, date: datetime) -> str:
        """Генерирует ключ для сегодняшнего челленджа."""
        return f"{date.year}-{date.month:02d}-{date.day:02d}"

    def __repr__(self) -> str:
        return f"<DailyChallenge(user_id={self.user_id}, date={self.date})>"