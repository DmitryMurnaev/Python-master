"""
app/templating.py
=================
Единый шаблонизатор Jinja2 для всего приложения.
"""

import os
import jinja2
from fastapi.responses import HTMLResponse

# Вычисляем абсолютный путь к директории templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

print(f"Templates directory: {TEMPLATES_DIR}")
print(f"Templates contents: {os.listdir(TEMPLATES_DIR)}")

# Создаём Jinja2 Environment
file_loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
env = jinja2.Environment(
    loader=file_loader,
    autoescape=True,
    cache_size=0,
)


def format_xp(xp: int) -> str:
    """Форматирует XP с разделением тысяч."""
    return f"{xp:,}".replace(",", " ")


env.filters["format_xp"] = format_xp


def render(template_name: str, context: dict) -> HTMLResponse:
    """Рендерит шаблон и возвращает HTMLResponse."""
    template = env.get_template(template_name)
    return HTMLResponse(template.render(**context))