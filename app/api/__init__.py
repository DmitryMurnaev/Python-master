"""
app/api/__init__.py
==================
Все API роутеры приложения.
"""

from app.api.auth import router as auth_router
from app.api.blocks import router as blocks_router
from app.api.tasks import router as tasks_router
from app.api.quiz import router as quiz_router
from app.api.progress import router as progress_router
from app.api.interpreter import router as interpreter_router
from app.api.flashcards import router as flashcards_router

__all__ = [
    "auth_router",
    "blocks_router",
    "tasks_router",
    "quiz_router",
    "progress_router",
    "interpreter_router",
    "flashcards_router",
]