"""
app/main.py
===========
Главный файл приложения FastAPI.

Здесь происходит:
1. Инициализация FastAPI приложения
2. Подключение роутеров
3. Настройка шаблонизатора Jinja2
4. Инициализация базы данных
5. Запуск сервера через Uvicorn
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
import os

from app.core.config import settings
from app.db.session import init_db, AsyncSessionLocal
from app.models import User, Block, Lesson, UserProgress, Task, Quiz, QuizResult, TaskSubmission, Achievement, UserAchievement
from app.api import (
    auth_router,
    blocks_router,
    tasks_router,
    quiz_router,
    progress_router,
    interpreter_router,
    flashcards_router,
)
from app.services.gamification import create_default_achievements, update_streak


# Настраиваем пути для статики и шаблонов
# os.path.abspath(__file__) = C:\...\Python-master\app\main.py
# dirname = C:\...\Python-master\app
# dirname again = C:\...\Python-master (проект)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
STATIC_DIR = os.path.join(APP_DIR, "static")

# Создаём директории если их нет
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events - выполняется при старте и остановке приложения.

    Здесь инициализируем базу данных и создаём начальные данные.
    """
    # Startup
    print("Инициализация базы данных...")
    await init_db()

    # Создаём достижения по умолчанию
    async with AsyncSessionLocal() as db:
        await create_default_achievements(db)

    print("База данных готова!")

    # Запускаем seed данных если нужно
    from app.db.seed import seed_initial_data
    async with AsyncSessionLocal() as db:
        await seed_initial_data(db)

    yield

    # Shutdown
    print("Приложение останавливается...")


# Создаём приложение FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Интерактивная платформа для изучения Python с нуля до уверенного уровня",
    version="1.0.0",
    lifespan=lifespan,
)

# Настраиваем CORS для будущего React фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статику
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Настраиваем Jinja2 шаблонизатор
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Добавляем фильтр для Jinja для красивого форматирования
def format_xp(xp: int) -> str:
    """Форматирует XP с разделением тысяч."""
    return f"{xp:,}".replace(",", " ")


templates.env.filters["format_xp"] = format_xp


# Подключаем API роутеры
app.include_router(auth_router)
app.include_router(blocks_router)
app.include_router(tasks_router)
app.include_router(quiz_router)
app.include_router(progress_router)
app.include_router(interpreter_router)
app.include_router(flashcards_router)


# Главная страница
@app.get("/favicon.ico")
async def favicon():
    """Заглушка для favicon."""
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница с информацией о курсе."""
    token = request.cookies.get("access_token")
    user_data = None

    if token:
        from app.core.security import decode_access_token
        user_id = decode_access_token(token)
        if user_id:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(User).where(User.id == int(user_id)))
                user = result.scalar_one_or_none()
                if user:
                    user_data = {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "xp": user.xp,
                        "level": user.level,
                    }

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user_data,
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Страница дашборда."""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)

    from app.core.security import decode_access_token
    user_id = decode_access_token(token)
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=302)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            return RedirectResponse(url="/auth/login", status_code=302)

        # Обновляем streak
        await update_streak(db, user)

        # Получаем статистику
        total_lessons = await db.execute(select(func.count(Lesson.id)))
        total_lessons_count = total_lessons.scalar() or 0

        total_tasks = await db.execute(select(func.count(Task.id)))
        total_tasks_count = total_tasks.scalar() or 0

        total_quizzes = await db.execute(select(func.count(Quiz.id)))
        total_quizzes_count = total_quizzes.scalar() or 0

        # Прогресс
        completed_result = await db.execute(
            select(func.count(UserProgress.id))
            .where(UserProgress.user_id == user.id)
            .where(UserProgress.is_completed == True)
        )
        completed_lessons = completed_result.scalar() or 0

        # Решённые задачи
        solved_result = await db.execute(
            select(func.count(TaskSubmission.id))
            .where(TaskSubmission.user_id == user.id)
            .where(TaskSubmission.result == 'PASS')
        )
        solved_tasks = solved_result.scalar() or 0

        # Пройденные квизы
        passed_result = await db.execute(
            select(func.count(QuizResult.id))
            .where(QuizResult.user_id == user.id)
            .where(QuizResult.is_passed == True)
        )
        passed_quizzes = passed_result.scalar() or 0

        # Достижения
        achievements_result = await db.execute(
            select(func.count(UserAchievement.id))
            .where(UserAchievement.user_id == user.id)
        )
        achievements_count = achievements_result.scalar() or 0

        # XP для следующего уровня
        from app.services.gamification import LEVELS
        current_level = user.level
        if current_level < 10:
            next_level_xp = LEVELS[current_level + 1]
            xp_to_next = next_level_xp - user.xp
            xp_in_level = user.xp - LEVELS[current_level]
            xp_needed = next_level_xp - LEVELS[current_level]
            xp_progress = int((xp_in_level / xp_needed) * 100) if xp_needed > 0 else 100
        else:
            xp_to_next = 0
            xp_progress = 100

        stats = {
            'total_xp': user.xp,
            'level': user.level,
            'xp_to_next_level': max(0, xp_to_next),
            'xp_progress_percent': xp_progress,
            'total_lessons': total_lessons_count,
            'completed_lessons': completed_lessons,
            'lessons_progress_percent': int((completed_lessons / total_lessons_count * 100)) if total_lessons_count > 0 else 0,
            'total_tasks': total_tasks_count,
            'solved_tasks': solved_tasks,
            'tasks_progress_percent': int((solved_tasks / total_tasks_count * 100)) if total_tasks_count > 0 else 0,
            'total_quizzes': total_quizzes_count,
            'passed_quizzes': passed_quizzes,
            'quizzes_progress_percent': int((passed_quizzes / total_quizzes_count * 100)) if total_quizzes_count > 0 else 0,
            'streak_days': user.streak_days,
            'achievements_count': achievements_count,
        }

        # Блоки
        blocks_result = await db.execute(select(Block).order_by(Block.order_index))
        blocks = blocks_result.scalars().all()

        # Прогресс по блокам
        blocks_progress = []
        for block in blocks:
            lessons_result = await db.execute(select(Lesson).where(Lesson.block_id == block.id))
            lessons = lessons_result.scalars().all()
            lesson_ids = [l.id for l in lessons]

            completed_in_block = await db.execute(
                select(func.count(UserProgress.id))
                .where(UserProgress.user_id == user.id)
                .where(UserProgress.lesson_id.in_(lesson_ids))
                .where(UserProgress.is_completed == True)
            )
            completed_count = completed_in_block.scalar() or 0

            blocks_progress.append({
                'block_id': block.id,
                'title': block.title,
                'icon': block.icon,
                'total_lessons': len(lessons),
                'completed_lessons': completed_count,
                'progress_percent': int((completed_count / len(lessons) * 100)) if lessons else 0,
            })

        # Достижения
        all_achievements_result = await db.execute(select(Achievement))
        all_achievements = all_achievements_result.scalars().all()

        user_achievements_result = await db.execute(
            select(UserAchievement).where(UserAchievement.user_id == user.id)
        )
        user_achievements = {ua.achievement_id for ua in user_achievements_result.scalars().all()}

        achievements_data = []
        for a in all_achievements[:6]:
            achievements_data.append({
                'code': a.code,
                'title': a.title,
                'description': a.description,
                'icon': a.icon,
                'is_earned': a.id in user_achievements,
            })

        # История активности (последние 7 дней)
        from datetime import datetime, timedelta
        activity = []
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            activity.append({
                'date': date.isoformat(),
                'xp_earned': 0,
                'lessons_completed': 0,
                'tasks_solved': 0,
            })

        next_goal = f"До следующего уровня: {xp_to_next} XP"

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user,
            "stats": stats,
            "blocks_progress": blocks_progress,
            "achievements": achievements_data,
            "earned_count": len(user_achievements),
            "activity": activity,
            "next_goal": next_goal,
        })


@app.get("/blocks", response_class=HTMLResponse)
async def blocks_page(request: Request):
    """Страница со списком блоков."""
    token = request.cookies.get("access_token")
    user = None

    if token:
        from app.core.security import decode_access_token
        user_id = decode_access_token(token)
        if user_id:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(User).where(User.id == int(user_id)))
                user = result.scalar_one_or_none()

    async with AsyncSessionLocal() as db:
        # Получаем блоки
        result = await db.execute(select(Block).order_by(Block.order_index))
        blocks = result.scalars().all()

        # Получаем прогресс пользователя
        user_progress = {}
        if user:
            result = await db.execute(
                select(UserProgress).where(UserProgress.user_id == user.id)
            )
            for p in result.scalars().all():
                user_progress[p.lesson_id] = p.is_completed

        blocks_data = []
        for block in blocks:
            # Получаем уроки блока
            result = await db.execute(select(Lesson).where(Lesson.block_id == block.id))
            lessons = result.scalars().all()

            completed = sum(1 for l in lessons if user_progress.get(l.id, False))

            blocks_data.append({
                'id': block.id,
                'title': block.title,
                'description': block.description,
                'icon': block.icon,
                'min_level': block.min_level,
                'xp_reward': block.xp_reward,
                'lessons_count': len(lessons),
                'completed_lessons': completed,
                'progress_percent': int((completed / len(lessons) * 100)) if lessons else 0,
            })

    return templates.TemplateResponse("blocks/blocks.html", {
        "request": request,
        "blocks": blocks_data,
        "user": user,
    })


# Обработка ошибок
@app.exception_handler(404)
async def not_found(request: Request, exc):
    """Страница 404."""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 404,
        "error_message": "Страница не найдена",
    }, status_code=404)


@app.exception_handler(500)
async def server_error(request: Request, exc):
    """Страница 500."""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 500,
        "error_message": "Внутренняя ошибка сервера",
    }, status_code=500)


# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )