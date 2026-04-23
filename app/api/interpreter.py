"""
app/api/interpreter.py
======================
Роутер для встроенного Python интерпретатора.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.interpreter import InterpreterRequest, InterpreterResponse
from app.services.interpreter import interpreter

router = APIRouter(prefix="/api/interpreter", tags=["interpreter"])


@router.post("/execute")
async def execute_code(
    request: InterpreterRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Выполнить Python код в безопасной среде.

    Args:
        request: Код для выполнения

    Returns:
        InterpreterResponse с результатом выполнения
    """
    result = interpreter.execute(request.code)

    return InterpreterResponse(
        success=result['success'],
        output=result['output'],
        error=result.get('error'),
        execution_time_ms=result['execution_time_ms'],
    )


@router.post("/test")
async def run_tests(
    code: str,
    test_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Выполнить тесты для проверки решения.

    Args:
        code: Код решения
        test_code: Тесты для проверки

    Returns:
        Результаты тестов
    """
    result = interpreter.run_tests(code, test_code)

    return {
        'success': result['success'],
        'output': result['output'],
        'error': result.get('error'),
        'tests_passed': result.get('tests_passed', 0),
        'tests_total': result.get('tests_total', 0),
        'execution_time_ms': result['execution_time_ms'],
    }


@router.post("/check-output")
async def check_output(
    code: str,
    expected_output: str,
    current_user: User = Depends(get_current_user)
):
    """
    Проверить вывод программы.

    Args:
        code: Код решения
        expected_output: Ожидаемый вывод

    Returns:
        Результат проверки
    """
    result = interpreter.check_output(code, expected_output)

    return result