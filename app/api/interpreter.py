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
from app.schemas.interpreter import InterpreterRequest, InterpreterResponse, InterpreterTestRequest, InterpreterCheckOutputRequest
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
    request: InterpreterTestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Выполнить тесты для проверки решения.

    Args:
        request: Код решения и тесты

    Returns:
        Результаты тестов
    """
    result = interpreter.run_tests(request.code, request.test_code)

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
    request: InterpreterCheckOutputRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Проверить вывод программы.

    Args:
        request: Код решения и ожидаемый вывод

    Returns:
        Результат проверки
    """
    result = interpreter.check_output(request.code, request.expected_output)

    return result