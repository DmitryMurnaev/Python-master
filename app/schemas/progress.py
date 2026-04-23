"""
app/schemas/progress.py
=======================
Pydantic схемы для прогресса и достижений.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ProgressStats(BaseModel):
    """Общая статистика прогресса."""
    total_xp: int = 0
    level: int = 1
    xp_to_next_level: int = 100
    xp_progress_percent: int = 0

    total_lessons: int = 0
    completed_lessons: int = 0
    lessons_progress_percent: int = 0

    total_tasks: int = 0
    solved_tasks: int = 0
    tasks_progress_percent: int = 0

    total_quizzes: int = 0
    passed_quizzes: int = 0
    quizzes_progress_percent: int = 0

    streak_days: int = 0
    achievements_count: int = 0


class BlockProgress(BaseModel):
    """Прогресс по конкретному блоку."""
    block_id: int
    title: str
    icon: str
    total_lessons: int
    completed_lessons: int
    progress_percent: int
    xp_earned: int = 0


class AchievementBase(BaseModel):
    """Базовая схема достижения."""
    title: str
    description: str
    icon: str = "🏆"
    xp_reward: int = 10


class AchievementResponse(AchievementBase):
    """Ответ с данными достижения."""
    id: int
    code: str
    is_earned: bool = False
    earned_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DailyChallengeResponse(BaseModel):
    """Ежедневный челлендж."""
    id: int
    task_id: int
    task_title: str
    date: datetime
    is_completed: bool
    xp_reward: int = 20


class LeaderboardEntry(BaseModel):
    """Запись в таблице лидеров."""
    rank: int
    username: str
    level: int
    xp: int
    streak_days: int


class ActivityDay(BaseModel):
    """День активности для графика."""
    date: str  # YYYY-MM-DD
    xp_earned: int = 0
    lessons_completed: int = 0
    tasks_solved: int = 0