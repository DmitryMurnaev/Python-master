"""
app/db/session.py
================
Настройка подключения к базе данных SQLAlchemy.

Архитектурные решения:
1. Используем async SQLAlchemy (asyncio) потому что:
   - FastAPI асинхронный, и БД операции должны быть неблокирующими
   - SQLite с aiosqlite позволяет обрабатывать больше запросов одновременно
   - Легко мигрировать на PostgreSQL (asyncpg) в продакшене

2. Используем dependency injection через Depends(get_db):
   - Каждый запрос получает свою сессию
   - Сессия автоматически закрывается после завершения запроса
   - Легко тестировать, подменяя get_db на mock

3. expire_on_commit=False:
   - После commit объект остаётся "присоединённым" к сессии
   - Это нужно для работы с объектами после закрытия транзакции
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Преобразуем postgresql:// в postgresql+asyncpg:// для асинхронного движка
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

# Создаём асинхронный движок базы данных
# check_same_thread=False нужен для SQLite при использовании в многопоточном контексте
connect_args = {}
if "sqlite" in database_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,  # Логируем SQL запросы в режиме отладки
    connect_args=connect_args
)

# Фабрика сессий - создаёт новую сессию для каждого запроса
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Сохраняем объекты после commit
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Наследуемся от DeclarativeBase - это современный стиль SQLAlchemy 2.0.
    Все модели должны наследоваться от этого класса.
    """
    pass


async def get_db() -> AsyncSession:
    """
    Dependency для получения сессии базы данных.

    Использование:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...

    FastAPI создаёт новую сессию для каждого запроса
    и автоматически закрывает её после завершения.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Коммитим изменения автоматически
        except Exception:
            await session.rollback()  # Откатываем при ошибке
            raise
        finally:
            await session.close()  # Закрываем сессию


async def init_db():
    """
    Инициализирует базу данных - создаёт все таблицы.

    Вызывается при старте приложения в main.py.

    Для миграций в будущем будем использовать Alembic,
    но для разработки и первоначального создания можно использовать этот метод.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)