"""
app/schemas/user.py
===================
Pydantic схемы для пользователей и аутентификации.

Эти схемы используются для:
1. Валидации входных данных (request body)
2. Сериализации ответов (response model)
3. Документации API (OpenAPI/Swagger)

Архитектурное решение: Разделяем Input и Output схемы
- Input (Create, Update) - для запросов
- Output (Response) - для ответов
Это позволяет контролировать, какие данные видит клиент.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Схема для входа (email + password)."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления профиля."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    theme: Optional[str] = None  # "dark" или "light"


class UserResponse(UserBase):
    """Схема ответа с данными пользователя."""
    id: int
    is_active: bool
    created_at: datetime
    xp: int
    level: int
    streak_days: int
    theme: str

    model_config = {"from_attributes": True}


class UserProfile(UserResponse):
    """Расширенный профиль пользователя со статистикой."""
    total_lessons_completed: int = 0
    total_tasks_solved: int = 0
    total_quizzes_passed: int = 0
    total_achievements: int = 0
    next_level_xp: int = 100  # XP для следующего уровня


class Token(BaseModel):
    """Схема JWT токена."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из токена (user_id)."""
    user_id: Optional[str] = None