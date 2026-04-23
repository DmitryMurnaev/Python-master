"""
app/core/config.py
==================
Конфигурация приложения с использованием Pydantic Settings.

Архитектурное решение: Используем pydantic-settings вместо os.environ.get()
Потому что это даёт:
1. Типобезопасность (валидация при старте приложения)
2. Документацию через типы
3. Поддержку .env файлов "из коробки"
4. Валидацию обязательных переменных

Для разработки используем SQLite (aiosqlite), для продакшена можно переключить на PostgreSQL.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения.

    Используем BaseSettings из pydantic-settings, которое автоматически
    читает переменные из .env файла (если он есть) или из окружения.
    """

    # Модель конфигурации - указываем откуда читать настройки
    model_config = SettingsConfigDict(
        env_file=".env",  # Ищем .env в корневой директории
        env_file_encoding="utf-8",
        case_sensitive=False,  # Регистр не важен для ключей
    )

    # Секретный ключ для JWT - обязательный параметр
    # В продакшене должен быть минимум 32 символа случайной строки
    SECRET_KEY: str = "dev-secret-key-change-in-production-minimum-32-chars"

    # Алгоритм для JWT - HS256 это стандартный и безопасный выбор
    ALGORITHM: str = "HS256"

    # Время жизни токена в минутах (1440 = 24 часа)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Режим отладки
    DEBUG: bool = True

    # Название проекта
    PROJECT_NAME: str = "Python Master"

    # Путь к базе данных SQLite
    # Используем file: для aiosqlite асинхронного драйвера
    DATABASE_URL: str = "sqlite+aiosqlite:///./python_master.db"

    # Настройки CORS (для будущего React фронтенда)
    # Позволяем запросы с localhost для разработки
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Максимальное время выполнения кода в интерпретаторе (секунды)
    INTERPRETER_TIMEOUT: int = 10

    # Максимальный размер вывода интерпретатора (символов)
    INTERPRETER_OUTPUT_LIMIT: int = 5000

    # Путь к Python интерпретатору (для subprocess)
    PYTHON_PATH: str = "python"  # Используем PATH системного Python


# Создаём глобальный экземпляр настроек
# Он будет использоваться во всём приложении
settings = Settings()