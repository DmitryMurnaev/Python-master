"""
app/templating.py
=================
Единый шаблонизатор Jinja2 для всего приложения.

Импортируется из main.py и используется во всех API роутерах.
"""

import os
from fastapi.templating import Jinja2Templates

# Вычисляем абсолютный путь к директории templates
# os.path.abspath(__file__) = C:\...\Python-master\app\templating.py
# dirname = C:\...\Python-master\app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Создаём единый экземпляр шаблонизатора
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Отключаем кэширование шаблонов
templates.env.cache = None


def format_xp(xp: int) -> str:
    """Форматирует XP с разделением тысяч."""
    return f"{xp:,}".replace(",", " ")


# Добавляем фильтр для Jinja
templates.env.filters["format_xp"] = format_xp