"""
app/core/security.py
====================
Модуль безопасности: работа с JWT токенами и паролями.

Архитектурные решения:
1. Используем JWT вместо сессий, потому что:
   - JWT stateless - не нужно хранить состояние на сервере
   - Легко масштабируется на несколько серверов
   - Можно передавать информацию о пользователе в самом токене

2. Используем bcrypt для хеширования паролей, потому что:
   - Создан специально для хеширования паролей
   - Защищён от rainbow table атак (есть salt)
   - Работает медленно, что защищает от брутфорса

3. Почему не сессии?
   - Сессии требуют Redis или другого хранилища
   - При масштабировании нужна синхронизация между серверами
   - JWT проще для API-first архитектуры (можно использовать и для будущего React приложения)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


# Контекст для хеширования паролей с bcrypt
# bcrypt автоматически добавляет salt, поэтому хранить его отдельно не нужно
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 схема для извлечения токена из заголовка Authorization
# FastAPI автоматически проверяет формат "Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль против хеша.

    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хеш из базы данных

    Returns:
        True если пароль верный, False если нет
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширует пароль с помощью bcrypt.

    Args:
        password: Пароль в открытом виде

    Returns:
        Хеш пароля, готовый для хранения в БД
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT access токен.

    Args:
        data: Данные для хранения в токене (обычно {"sub": user_id})
        expires_delta: Опциональное время жизни токена

    Returns:
        Закодированный JWT токен

    Пример структуры JWT:
    {
        "sub": "1",           # user_id
        "exp": 1234567890,    # время истечения
        "iat": 1234567800     # время создания
    }
    """
    # Копируем данные, чтобы не мутировать входящий словарь
    to_encode = data.copy()

    # Вычисляем время истечения
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Добавляем стандартные поля JWT
    to_encode.update({
        "exp": expire,  # expiration time
        "iat": datetime.now(timezone.utc),  # issued at
    })

    # Кодируем в JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Декодирует JWT токен и возвращает user_id.

    Args:
        token: JWT токен

    Returns:
        user_id если токен валидный, None если истёк или невалидный
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None


async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    Зависимость для получения текущего пользователя.
    Сначала ищет токен в заголовке Authorization: Bearer <token>,
    затем в cookie 'access_token'.
    """
    token = None

    # Пытаемся взять из заголовка
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Иначе из cookie
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не найден токен доступа",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Некорректный ID пользователя")

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


async def get_current_user_optional(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Опциональная версия — возвращает None, если не удалось аутентифицировать.
    """
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("access_token")

    if not token:
        return None

    user_id = decode_access_token(token)
    if user_id is None:
        return None

    try:
        user_id_int = int(user_id)
    except ValueError:
        return None

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()
    return user