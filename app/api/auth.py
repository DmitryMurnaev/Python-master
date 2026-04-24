"""
app/api/auth.py
===============
Роутер аутентификации: регистрация, вход, выход.

Архитектурное решение: Используем JWT токены вместо сессий.
Почему JWT:
1. Stateless - не нужно хранить состояние на сервере
2. Легко масштабируется (не нужен Redis для сессий)
3. Можно использовать и для будущего мобильного приложения или React фронтенда
4. Проще в реализации и понимании

Недостатки JWT:
1. Нельзя "отозвать" токен до истечения срока (нужно добавлять blacklist)
2. Размер больше чем session ID

Для данного учебного проекта JWT недостатки не критичны.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    oauth2_scheme,
)
from app.core.config import settings
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserProfile, Token
from app.services.gamification import update_streak
from app.templating import templates

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/register")
async def register_page(request):
    """Страница регистрации."""
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.

    Args:
        username: Имя пользователя
        email: Email
        password: Пароль (будет хеширован)
        db: Сессия БД
    """
    # Проверяем что пользователь с таким email ещё не существует
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    # Проверяем что username свободен
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже занято"
        )

    # Создаём нового пользователя
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Создаём JWT токен
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Редиректим на дашборд
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    return response


@router.get("/login")
async def login_page(request):
    """Страница входа."""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Вход пользователя.

    Args:
        email: Email
        password: Пароль
        db: Сессия БД
    """
    # Ищем пользователя
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован"
        )

    # Обновляем streak
    await update_streak(db, user)

    # Создаём токен
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Редиректим
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    return response


@router.post("/logout")
async def logout():
    """Выход из системы."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе.

    Args:
        current_user: Текущий пользователь из JWT токена
    """
    return UserResponse.model_validate(current_user)


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить расширенный профиль пользователя со статистикой.
    """
    from app.models.progress import UserProgress, QuizResult, TaskSubmission, UserAchievement
    from app.models.learning import Lesson, Quiz, Task
    from sqlalchemy import func

    # Получаем статистику
    lessons_completed = await db.execute(
        select(func.count(UserProgress.id))
        .where(UserProgress.user_id == current_user.id)
        .where(UserProgress.is_completed == True)
    )
    lessons_count = lessons_completed.scalar() or 0

    tasks_solved = await db.execute(
        select(func.count(TaskSubmission.id))
        .where(TaskSubmission.user_id == current_user.id)
        .where(TaskSubmission.result == 'PASS')
    )
    tasks_count = tasks_solved.scalar() or 0

    quizzes_passed = await db.execute(
        select(func.count(QuizResult.id))
        .where(QuizResult.user_id == current_user.id)
        .where(QuizResult.is_passed == True)
    )
    quizzes_count = quizzes_passed.scalar() or 0

    achievements_count = await db.execute(
        select(func.count(UserAchievement.id))
        .where(UserAchievement.user_id == current_user.id)
    )
    achievements = achievements_count.scalar() or 0

    # Считаем XP для следующего уровня
    from app.services.gamification import LEVELS, calculate_level
    current_level = current_user.level
    if current_level < 10:
        next_level_xp = LEVELS[current_level + 1]
    else:
        next_level_xp = LEVELS[current_level]

    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        xp=current_user.xp,
        level=current_user.level,
        streak_days=current_user.streak_days,
        theme=current_user.theme,
        total_lessons_completed=lessons_count,
        total_tasks_solved=tasks_count,
        total_quizzes_passed=quizzes_count,
        total_achievements=achievements,
        next_level_xp=next_level_xp,
    )


@router.put("/settings")
async def update_settings(
    theme: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить настройки пользователя.

    Args:
        theme: Тема оформления (dark/light)
    """
    if theme not in ('dark', 'light'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тема должна быть dark или light"
        )

    current_user.theme = theme
    await db.commit()

    return {"message": "Настройки обновлены", "theme": theme}