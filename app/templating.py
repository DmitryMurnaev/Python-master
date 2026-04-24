"""
app/templating.py
=================
Единый шаблонизатор Jinja2 для всего приложения.

Импортируется из main.py и используется во всех API роутерах.
"""

import os
import jinja2

# Вычисляем абсолютный путь к директории templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

print(f"Templates directory: {TEMPLATES_DIR}")
print(f"Templates contents: {os.listdir(TEMPLATES_DIR)}")

# Создаём Jinja2 Environment с отключенным кэшем
file_loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
env = jinja2.Environment(
    loader=file_loader,
    autoescape=True,
    cache_size=0,  # Отключаем кэширование
)


# Кастомный класс для совместимости с FastAPI
class Jinja2Templates:
    """Обёртка для Jinja2 - совместима с TemplateResponse."""

    def __init__(self, directory: str = None):
        self.env = env
        self.directory = directory

    def TemplateResponse(self, name: str, context: dict):
        """Рендерит шаблон и возвращает HTMLResponse."""
        from fastapi.responses import HTMLResponse
        template = self.env.get_template(name)
        return HTMLResponse(template.render(**context))


templates = Jinja2Templates(directory=TEMPLATES_DIR)


def format_xp(xp: int) -> str:
    """Форматирует XP с разделением тысяч."""
    return f"{xp:,}".replace(",", " ")


# Добавляем фильтр для Jinja
templates.env.filters["format_xp"] = format_xp