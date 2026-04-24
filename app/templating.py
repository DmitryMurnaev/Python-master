"""
app/templating.py
=================
Единый шаблонизатор Jinja2 для всего приложения.

Импортируется из main.py и используется во всех API роутерах.
"""

import os
import jinja2

# Вычисляем абсолютный путь к директории templates
# os.path.abspath(__file__) = C:\...\Python-master\app\templating.py
# dirname = C:\...\Python-master\app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Создаём FileSystemLoader
file_loader = jinja2.FileSystemLoader(TEMPLATES_DIR)

# Создаём Environment с отключённым кэшированием
env = jinja2.Environment(
    loader=file_loader,
    autoescape=True,
    cache_size=0,  # Отключаем кэш
)

# Функция для рендеринга шаблона
def render_template(template_name: str, context: dict):
    """Рендерит шаблон и возвращает HTML строку."""
    template = env.get_template(template_name)
    return template.render(**context)


# Класс совместимый с FastAPI TemplateResponse
class Jinja2Templates:
    """Обёртка для совместимости с FastAPI."""

    def __init__(self, directory: str = None):
        self.directory = directory
        self.env = env

    def TemplateResponse(self, name: str, context: dict):
        """Возвращает HTMLResponse с отрендеренным шаблоном."""
        from fastapi.responses import HTMLResponse
        template = self.env.get_template(name)
        return HTMLResponse(template.render(**context))


templates = Jinja2Templates(directory=TEMPLATES_DIR)


def format_xp(xp: int) -> str:
    """Форматирует XP с разделением тысяч."""
    return f"{xp:,}".replace(",", " ")


# Добавляем фильтр для Jinja
templates.env.filters["format_xp"] = format_xp