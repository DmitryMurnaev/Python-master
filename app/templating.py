"""
app/templating.py
=================
Единый шаблонизатор Jinja2 для всего приложения.

Импортируется из main.py и используется во всех API роутерах.
"""

import os
from fastapi.templating import Jinja2Templates

# Вычисляем абсолютный путь к директории templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# DEBUG: проверяем что директория существует
import os
if not os.path.exists(TEMPLATES_DIR):
    print(f"WARNING: Templates directory not found: {TEMPLATES_DIR}")
    # Пробуем альтернативный путь
    ALT_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")
    if os.path.exists(ALT_DIR):
        TEMPLATES_DIR = ALT_DIR
        print(f"Using alternative templates dir: {TEMPLATES_DIR}")
else:
    print(f"Templates directory found: {TEMPLATES_DIR}")
    print(f"Templates contents: {os.listdir(TEMPLATES_DIR)}")

# Создаём единый экземпляр шаблонизатора
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Отключаем кэширование
templates.env.cache = None


def format_xp(xp: int) -> str:
    """Форматирует XP с разделением тысяч."""
    return f"{xp:,}".replace(",", " ")


# Добавляем фильтр для Jinja
templates.env.filters["format_xp"] = format_xp