"""
app/core/__init__.py
===================
Ядро приложения - конфигурация и безопасность.

Модули:
- config.py: Настройки приложения (Settings)
- security.py: JWT токены, пароли, аутентификация

Импортируйте отсюда всё для удобства:
    from app.core import settings, get_password_hash, create_access_token
"""

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    get_current_user,
    get_current_user_optional,
    oauth2_scheme,
)

__all__ = [
    "settings",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_current_user_optional",
    "oauth2_scheme",
]