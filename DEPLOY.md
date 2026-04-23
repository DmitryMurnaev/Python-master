# Запуск и Деплой Python Master

## Локальный запуск (Windows)

```bash
cd Python-master

# Создать виртуальное окружение (Python 3.11)
python -m venv venv
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запуск
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте http://localhost:8000

**Важно**: Требуется Python 3.11 (не 3.14!) - иначе будет ошибка с Jinja2.

## Docker запуск

```bash
# Собрать образ
docker build -t python-master .

# Запуск (данные сохраняются в ./data)
docker run -d -p 8000:8000 --name python-master -v $(pwd)/data:/data python-master

# Или через docker-compose
docker-compose up -d
```

## Деплой в облако

### Render.com (бесплатный tier)
1. Создайте аккаунт на render.com
2. Подключите GitHub репозиторий
3. Создайте Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Environment: Python 3.11

### Railway.app
1. Создайте проект
2. Добавьте Postgres database (бесплатно)
3. Задеплойте из GitHub
4. Установите переменную DATABASE_URL

### Fly.io
```bash
fly launch
fly deploy
```

## Переменные окружения (.env)

```env
SECRET_KEY=ваш-секретный-ключминимум-32-символа
DEBUG=false
DATABASE_URL=sqlite+aiosqlite:///data/python_master.db
```

## Структура файлов для деплоя

```
Python-master/
├── Dockerfile          # для Docker деплоя
├── docker-compose.yml  # для локального Docker
├── requirements.txt    # зависимости Python
├── .env                # секреты (НЕ коммитить!)
└── app/                # код приложения
```

## Доступ с телефона/планшета

После деплоя на облако (Render/Railway/Fly) приложение будет доступно по URL типа:
- `https://your-app.onrender.com`
- `https://your-app.railway.app`

Это работает с любого устройства с браузером.

## Если нужна база данных PostgreSQL

В `.env` измените:
```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

И добавьте в requirements.txt:
```
asyncpg>=0.27.0
```