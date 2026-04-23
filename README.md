# Python Master - Интерактивная платформа для изучения Python

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## О проекте

**Python Master** — это интерактивная образовательная платформа для изучения Python с нуля до уверенного уровня. Создана для начинающих разработчиков, которые хотят освоить Python через практику.

### Возможности

- 📚 **8 структурированных блоков обучения** — от основ до продвинутых тем
- 💻 **Встроенный Python интерпретатор** — пишите и запускайте код прямо в браузере
- 🎯 **Автоматическая проверка задач** — получайте мгновенную обратную связь
- 📊 **Система прогресса** — XP, уровни, достижения для мотивации
- 🔥 **Streak система** — мотивирует заниматься каждый день
- 🃏 **Карточки для повторения** — алгоритм интервального повторения SM-2
- 🏆 **Достижения и бейджи** — получайте награды за прогресс

## Технологии

- **Backend**: FastAPI + Python 3.11+
- **База данных**: SQLite + SQLAlchemy (async)
- **Frontend**: Jinja2 + Tailwind CSS
- **Аутентификация**: JWT токены

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/DmitryMurnaev/Python-master.git
cd Python-master
```

### 2. Создание виртуального окружения

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` файл если нужно изменить SECRET_KEY.

### 5. Запуск сервера

```bash
# Вариант 1: напрямую
python -m app.main

# Вариант 2: через uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Открытие в браузере

Перейдите на [http://localhost:8000](http://localhost:8000)

Для входа используйте демо-аккаунт:
- **Email**: demo@example.com
- **Password**: demo123

## Структура проекта

```
Python-master/
├── app/
│   ├── api/              # API роутеры
│   │   ├── auth.py       # Аутентификация
│   │   ├── blocks.py     # Блоки и уроки
│   │   ├── tasks.py      # Задачи
│   │   ├── quiz.py       # Квизы
│   │   ├── flashcards.py # Карточки
│   │   └── progress.py   # Прогресс
│   ├── core/             # Ядро приложения
│   │   ├── config.py     # Конфигурация
│   │   └── security.py   # Безопасность (JWT, passwords)
│   ├── db/               # Работа с БД
│   │   ├── session.py    # Подключение к БД
│   │   └── seed.py       # Начальные данные
│   ├── models/           # SQLAlchemy модели
│   │   ├── user.py       # Пользователь
│   │   ├── learning.py   # Блоки, уроки, задачи
│   │   ├── progress.py   # Прогресс, достижения
│   │   └── flashcard.py  # Карточки
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   │   ├── interpreter.py # Python интерпретатор
│   │   └── gamification.py # XP, уровни, достижения
│   └── templates/        # HTML шаблоны (Jinja2)
├── static/               # Статические файлы
├── alembic/              # Миграции БД
└── requirements.txt      # Зависимости
```

## Архитектурные решения

### Почему JWT вместо сессий?

1. **Stateless** — не нужно хранить состояние на сервере
2. **Масштабируемость** — легко масштабировать на несколько серверов
3. **Простота** — проще в реализации чем сессии с Redis

### Почему SQLite?

Для разработки и учебного проекта SQLite — идеальный выбор:
- Не требует установки сервера
- Отлично работает с async SQLAlchemy
- Легко мигрировать на PostgreSQL в будущем

### Почему Jinja2, а не React?

На данном этапе:
- Проще для понимания и отладки
- Быстрая разработка без сборки
- Легко добавить React позже как отдельный фронтенд

## API Endpoints

### Аутентификация
- `GET /auth/register` — страница регистрации
- `POST /auth/register` — регистрация
- `GET /auth/login` — страница входа
- `POST /auth/login` — вход
- `POST /auth/logout` — выход

### Блоки и уроки
- `GET /api/blocks/` — список блоков
- `GET /api/blocks/{id}` — детали блока
- `GET /api/blocks/lesson/{id}` — страница урока

### Задачи
- `POST /api/tasks/{id}/submit` — отправить решение
- `POST /api/tasks/{id}/run` — запустить код

### Квизы
- `GET /api/quiz/{id}` — получить квиз
- `POST /api/quiz/{id}/submit` — отправить ответы

### Карточки
- `GET /api/flashcards/study` — получить карточки на изучение
- `POST /api/flashcards/review` — оценить карточку

### Интерпретатор
- `POST /api/interpreter/execute` — выполнить код

## Дальнейшее развитие

### Добавить React фронтенд

1. Создать отдельный репозиторий или папку `frontend/`
2. Использовать Vite для сборки
3. Подключить API через fetch/axios
4. Использовать JWT токен из cookie

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Деплой

- **Railway** — простой деплой с Postgres
- **Render** — бесплатный tier для Python
- **Fly.io** — контейнеры с persistence

## Лицензия

MIT License — используйте свободно для обучения и своих проектов.

## Автор

Dmitry Murnaev — Python разработчик, создано для изучения Python.

---

⭐ Если проект полезен, поставьте звезду на GitHub!