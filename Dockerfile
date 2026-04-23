# Dockerfile для Python Master
# Используем python:3.11-slim для уменьшения размера образа

FROM python:3.11-slim

# Создаём рабочую директорию
WORKDIR /app

# Копируем только requirements сначала (для кэширования слоя)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё остальное
COPY . .

# Создаём директорию для данных
RUN mkdir -p /data

# Переменные окружения
ENV DATABASE_URL="sqlite+aiosqlite:////data/python_master.db"
ENV DEBUG="false"
ENV PYTHONUNBUFFERED="1"

# Порт
EXPOSE 8000

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]