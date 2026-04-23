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
from fastapi import Depends, HTTPException, status
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
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Зависимость FastAPI для получения текущего пользователя из токена.

    Используется какDepends() в эндпоинтах, требующих аутентификации.

    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных

    Returns:
        Объект User

    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Декодируем токен
    user_id = decode_access_token(token)

    if user_id is None:
        raise credentials_exception

    # Ищем пользователя в базе
    # user_id пришёл как строка из JWT, приводим к int
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Опциональная версия get_current_user - не выбрасывает исключение,
    а возвращает None если пользователь не аутентифицирован.

    Используется для страниц, где гости тоже могут просматривать контент.
    """
    if not token:
        return None

    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None