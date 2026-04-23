"""
app/services/__init__.py
=======================
Сервисы приложения.
"""

from app.services.interpreter import PythonInterpreter, interpreter, execute_code
from app.services.gamification import (
    LEVELS,
    XP_REWARDS,
    calculate_level,
    xp_for_next_level,
    update_user_xp,
    update_streak,
    check_achievements,
    create_default_achievements,
    ACHIEVEMENTS_DATA,
)

__all__ = [
    "PythonInterpreter",
    "interpreter",
    "execute_code",
    "LEVELS",
    "XP_REWARDS",
    "calculate_level",
    "xp_for_next_level",
    "update_user_xp",
    "update_streak",
    "check_achievements",
    "create_default_achievements",
    "ACHIEVEMENTS_DATA",
]