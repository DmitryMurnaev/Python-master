"""
app/schemas/interpreter.py
==========================
Схемы для встроенного Python интерпретатора.
"""

from pydantic import BaseModel, Field
from typing import Optional


class InterpreterRequest(BaseModel):
    """Запрос на выполнение кода."""
    code: str = Field(..., min_length=1, max_length=50000)
    task_id: Optional[int] = None  # Если выполняется в контексте задачи


class InterpreterResponse(BaseModel):
    """Результат выполнения кода."""
    success: bool
    output: str = ""
    error: Optional[str] = None
    execution_time_ms: int = 0
    memory_used_kb: Optional[int] = None  # Если удастся измерить


class InterpreterError(BaseModel):
    """Ошибка интерпретатора."""
    error: str
    error_type: str  # SyntaxError, RuntimeError, TimeoutError, etc.
    line: Optional[int] = None