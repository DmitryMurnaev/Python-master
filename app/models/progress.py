"""
app/models/progress.py
====================
Модели для отслеживания прогресса пользователя.

Включает:
- UserProgress: Прогресс по урокам/квизам/задачам
- QuizResult: Результаты прохождения квизов
- TaskSubmission: Решения задач
- Achievement: Достижения (бейджи)
- UserAchievement: Связь пользователя с достижениями
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.session import Base


class UserProgress(Base):
    """
    Отслеживание прогресса пользователя по урокам.

    Записываем:
    - Какие уроки пройдены
    - Сколько времени потрачено
    - Когда последний раз открывал
    """
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="progress")
    lesson: Mapped["Lesson"] = relationship("Lesson")

    def __repr__(self) -> str:
        return f"<UserProgress(user_id={self.user_id}, lesson_id={self.lesson_id})>"


class QuizResult(Base):
    """
    Результат прохождения квиза.

    Сохраняем историю всех попыток - это полезно для анализа
    и для показа "лучший результат".
    """
    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # Процент правильных
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    is_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="quiz_results")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="results")

    def __repr__(self) -> str:
        return f"<QuizResult(user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score}%)>"


class TaskSubmission(Base):
    """
    Решение задачи пользователем.

    Сохраняем:
    - Код пользователя
    - Результат проверки (PASS/FAIL)
    - Вывод интерпретатора
    - Время выполнения
    """
    __tablename__ = "task_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # PASS, FAIL, ERROR
    output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tests_passed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tests_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="task_submissions")
    task: Mapped["Task"] = relationship("Task", back_populates="submissions")

    def __repr__(self) -> str:
        return f"<TaskSubmission(user_id={self.user_id}, task_id={self.task_id}, result={self.result})>"


class Achievement(Base):
    """
    Достижение (бейдж) в системе.

    Предопределённые достижения создаются при инициализации БД.
    """
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(20), default="🏆")
    xp_reward: Mapped[int] = mapped_column(Integer, default=10)

    # Условие получения (JSON строка с критериями)
    criteria: Mapped[str] = mapped_column(Text, nullable=True)

    # Связи
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Achievement(code={self.code}, title={self.title})>"


class UserAchievement(Base):
    """
    Связь пользователя с полученными достижениями.

    Многие ко многим через эту таблицу.
    """
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"