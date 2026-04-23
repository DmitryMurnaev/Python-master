"""
app/models/learning.py
=====================
Модели для структуры обучения: блоки, уроки, теория.

Блок (Block) -> Урок (Lesson) -> Теория (Theory)
                                              -> Квиз (Quiz)
                                              -> Задача (Task)
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.session import Base


class Block(Base):
    """
    Блок обучения - крупная тема (например "Основы Python").

    Структура:
    - Порядковый номер для сортировки
    - Название и описание
    - Иконка (emoji) для визуализации
    - Привязка к уровню (какой уровень нужен для начала)
    """
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(10), default="📚")
    min_level: Mapped[int] = mapped_column(Integer, default=1)  # Минимальный уровень для доступа

    # XP за прохождение блока
    xp_reward: Mapped[int] = mapped_column(Integer, default=50)

    # Связи
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="block", cascade="all, delete-orphan"
    )

    @property
    def total_lessons(self) -> int:
        """Возвращает общее количество уроков в блоке."""
        return len(self.lessons)

    def __repr__(self) -> str:
        return f"<Block(id={self.id}, title={self.title})>"


class Lesson(Base):
    """
    Урок - конкретная тема внутри блока (например "Переменные и типы данных").

    Каждый урок содержит:
    - Теорию (текст + примеры кода)
    - Квиз для проверки
    - Несколько практических задач
    - Проект (большая задача в конце блока)
    """
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    block_id: Mapped[int] = mapped_column(Integer, ForeignKey("blocks.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Markdown теория
    is_project: Mapped[bool] = mapped_column(Boolean, default=False)  # Это проект урока?

    # XP за успешное выполнение
    xp_reward: Mapped[int] = mapped_column(Integer, default=30)

    # Связи
    block: Mapped["Block"] = relationship("Block", back_populates="lessons")
    quizzes: Mapped[list["Quiz"]] = relationship(
        "Quiz", back_populates="lesson", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="lesson", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, title={self.title})>"


class Quiz(Base):
    """
    Квиз - набор вопросов для проверки понимания теории.

    Вопросы хранятся в виде JSON строки для простоты.
    Структура вопроса:
    {
        "question": "Текст вопроса",
        "options": ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
        "correct": 0  # Индекс правильного ответа
    }
    """
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    questions: Mapped[str] = mapped_column(Text, nullable=False)  # JSON строка

    # Минимальный процент правильных ответов для прохождения
    passing_score: Mapped[float] = mapped_column(Float, default=70.0)

    # Связи
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="quizzes")
    results: Mapped[list["QuizResult"]] = relationship(
        "QuizResult", back_populates="quiz", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, title={self.title})>"


class Task(Base):
    """
    Практическая задача - требует от пользователя написать код.

    Структура:
    - description: Условие задачи
    - starter_code: Начальный код (если есть)
    - solution: Эталонное решение (для проверки преподавателем)
    - test_code: Код для автоматической проверки (unittest)
    - expected_output: Ожидаемый вывод (для простой проверки вывода)
    - hints: Подсказки (массив строк)
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    test_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    xp_reward: Mapped[int] = mapped_column(Integer, default=30)

    # Связи
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="tasks")
    submissions: Mapped[list["TaskSubmission"]] = relationship(
        "TaskSubmission", back_populates="task", cascade="all, delete-orphan"
    )

    @property
    def hints_list(self) -> list[str]:
        """Возвращает подсказки в виде списка."""
        import json
        if self.hints:
            return json.loads(self.hints)
        return []

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title})>"