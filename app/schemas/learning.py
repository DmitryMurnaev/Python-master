"""
app/schemas/learning.py
=======================
Pydantic схемы для структуры обучения (блоки, уроки, задачи).
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class BlockBase(BaseModel):
    """Базовая схема блока."""
    title: str
    description: Optional[str] = None
    icon: str = "📚"
    min_level: int = 1
    xp_reward: int = 50


class BlockCreate(BlockBase):
    """Схема для создания блока."""
    order_index: int = 0


class BlockResponse(BlockBase):
    """Схема ответа с данными блока."""
    id: int
    order_index: int
    lessons_count: int = 0
    completed_lessons: int = 0
    progress_percent: int = 0

    model_config = {"from_attributes": True}


class BlockDetail(BlockResponse):
    """Детальная информация о блоке с уроками."""
    lessons: list["LessonResponse"] = []


class LessonBase(BaseModel):
    """Базовая схема урока."""
    title: str
    description: Optional[str] = None
    is_project: bool = False
    xp_reward: int = 30


class LessonCreate(LessonBase):
    """Схема для создания урока."""
    block_id: int
    order_index: int = 0
    content: Optional[str] = None


class LessonResponse(LessonBase):
    """Схема ответа с данными урока."""
    id: int
    block_id: int
    order_index: int
    is_completed: bool = False
    is_locked: bool = True  # Заблокирован пока не пройдены предыдущие
    quizzes_count: int = 0
    tasks_count: int = 0

    model_config = {"from_attributes": True}


class LessonDetail(LessonResponse):
    """Детальная информация об уроке с квизами и задачами."""
    content: Optional[str] = None
    quizzes: list["QuizResponse"] = []
    tasks: list["TaskResponse"] = []


class QuizBase(BaseModel):
    """Базовая схема квиза."""
    title: str
    passing_score: float = 70.0


class QuizCreate(QuizBase):
    """Схема для создания квиза."""
    lesson_id: int
    questions: str  # JSON строка


class QuizQuestion(BaseModel):
    """Схема вопроса квиза."""
    question: str
    options: list[str]
    correct: int  # Индекс правильного ответа


class QuizResponse(QuizBase):
    """Схема ответа с данными квиза."""
    id: int
    lesson_id: int
    questions_count: int = 0

    model_config = {"from_attributes": True}


class QuizSubmission(BaseModel):
    """Схема ответа на квиз."""
    answers: list[int] = Field(..., description="Список ответов: индексы выбранных вариантов")


class QuizResultResponse(BaseModel):
    """Результат прохождения квиза."""
    score: float
    correct_answers: int
    total_questions: int
    is_passed: bool
    xp_earned: int = 0


class TaskBase(BaseModel):
    """Базовая схема задачи."""
    title: str
    description: str
    starter_code: Optional[str] = None
    hints: Optional[str] = None  # JSON array
    xp_reward: int = 30


class TaskCreate(TaskBase):
    """Схема для создания задачи."""
    lesson_id: int
    order_index: int = 0
    test_code: Optional[str] = None
    expected_output: Optional[str] = None


class TaskResponse(TaskBase):
    """Схема ответа с данными задачи."""
    id: int
    lesson_id: int
    order_index: int
    is_solved: bool = False
    attempts_count: int = 0

    model_config = {"from_attributes": True}


class TaskDetail(TaskResponse):
    """Детальная информация о задаче."""
    solution: Optional[str] = None
    hints_list: list[str] = []


class TaskSubmissionCode(BaseModel):
    """Код, отправленный на проверку."""
    code: str = Field(..., min_length=1)


class TaskSubmissionResult(BaseModel):
    """Результат проверки задачи."""
    result: str  # PASS, FAIL, ERROR
    output: Optional[str] = None
    error_message: Optional[str] = None
    tests_passed: Optional[int] = None
    tests_total: Optional[int] = None
    xp_earned: int = 0
    is_final: bool = True  # Была ли это финальная попытка (для достижений)


# Обновляем forward references для рекурсивных схем
BlockDetail.model_rebuild()
LessonDetail.model_rebuild()