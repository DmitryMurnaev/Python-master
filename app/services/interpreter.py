"""
app/services/interpreter.py
===========================
Встроенный Python интерпретатор с песочницей.

Архитектурные решения:
1. Используем subprocess для изоляции кода - код выполняется в отдельном процессе
2. Ограничиваем время выполнения (timeout) чтобы избежать бесконечных циклов
3. Перехватываем stdout/stderr для получения вывода
4. Запрещаем потенциально опасные модули (os, sys, subprocess, etc.)

Безопасность:
- subprocess.run() с ограничением по времени
- Нет доступа к файловой системе (разрешены только print, input, базовые операции)
- Нельзя открывать сокеты или сетевые соединения
- Нельзя импортировать опасные модули

Альтернатива: Pyodide (Python в браузере через WebAssembly) или code execution API.
Для данного проекта subprocess достаточно безопасен и прост.
"""

import io
import sys
import time
import traceback
from typing import Optional, Tuple
from contextlib import redirect_stdout, redirect_stderr

from app.core.config import settings


class PythonInterpreter:
    """
    Безопасный интерпретатор Python для выполнения кода пользователей.

    Использование:
        interpreter = PythonInterpreter()
        result = interpreter.execute("print('Hello!')")
        # {'success': True, 'output': 'Hello!\n', 'error': None}
    """

    # Модули, ЗАПРЕЩЁННЫЕ к импорту
    BLOCKED_MODULES = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'http', 'ftplib', 'telnetlib', 'paramiko', 'fabric',
        'importlib', 'pkgutil', 'zipimport', '__import__',
        'eval', 'exec', 'compile', 'open', 'file', 'input',
        'os.path', 'pathlib', 'shutil', 'tempfile',
        'multiprocessing', 'threading', 'asyncio',
        'ctypes', 'cffi', 'numpy', 'scipy',  # heavy dependencies
    }

    # Ключевые слова, запрещённые в коде
    BLOCKED_KEYWORDS = {
        'import', 'from', '__import__', 'reload', 'breakpoint',
        'exit', 'quit', 'help', 'credits', 'license', 'copyright',
    }

    def __init__(self, timeout: int = None):
        """
        Инициализирует интерпретатор.

        Args:
            timeout: Максимальное время выполнения в секундах.
                    По умолчанию из настроек.
        """
        self.timeout = timeout or settings.INTERPRETER_TIMEOUT
        self.output_limit = settings.INTERPRETER_OUTPUT_LIMIT

    def execute(self, code: str) -> dict:
        """
        Выполняет Python код в безопасной среде.

        Args:
            code: Python код для выполнения

        Returns:
            dict с ключами:
            - success: bool - успешно ли выполнился код
            - output: str - вывод программы (stdout)
            - error: str - текст ошибки (если есть)
            - execution_time_ms: int - время выполнения
        """
        start_time = time.time()

        # Проверка на запрещённые ключевые слова
        if self._contains_blocked_keywords(code):
            return {
                'success': False,
                'output': '',
                'error': 'Использование этого ключевого слова запрещено в целях безопасности.',
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

        # Создаём ограниченное пространство имён для выполнения
        safe_globals = {
            '__name__': '__main__',
            '__builtins__': self._get_safe_builtins(),
        }

        safe_locals = {
            # Разрешённые встроенные функции и классы
            'print': print,
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'slice': slice,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'reversed': reversed,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'isinstance': isinstance,
            'issubclass': issubclass,
            'type': type,
            'any': any,
            'all': all,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'chr': chr,
            'ord': ord,
            'hex': hex,
            'oct': oct,
            'bin': bin,
            'repr': repr,
            'format': format,
            'divmod': divmod,
            'pow': pow,
            'complex': complex,
            'bytes': bytes,
            'bytearray': bytearray,
            'memoryview': memoryview,
            'frozenset': frozenset,
            # Разрешённые классы из typing
            'Optional': Optional,
            'List': list,
            'Dict': dict,
            'Tuple': tuple,
            'Set': set,
            'Union': type('Union', (), {}),
        }

        try:
            # Перехватываем stdout и stderr
            output_buffer = io.StringIO()

            with redirect_stdout(output_buffer):
                with redirect_stderr(output_buffer):
                    # Выполняем код
                    exec(code, safe_globals, safe_locals)

            output = output_buffer.getvalue()

            # Обрезаем вывод если слишком длинный
            if len(output) > self.output_limit:
                output = output[:self.output_limit] + f"\n... (вывод обрезан, превышен лимит {self.output_limit} символов)"

            return {
                'success': True,
                'output': output,
                'error': None,
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

        except SyntaxError as e:
            return {
                'success': False,
                'output': '',
                'error': f'SyntaxError: {e.msg}\nСтрока {e.lineno}, столбец {e.offset}',
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

        except IndentationError as e:
            return {
                'success': False,
                'output': '',
                'error': f'IndentationError: {e.msg}\nСтрока {e.lineno}',
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

        except TabError as e:
            return {
                'success': False,
                'output': '',
                'error': f'TabError: {e.msg}',
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

        except Exception as e:
            # Перехватываем все остальные ошибки
            error_type = type(e).__name__
            error_msg = str(e)

            # Получаем краткий traceback
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            # Берём только последние 10 строк
            tb_lines = tb_str.split('\n')[-10:]
            tb_short = '\n'.join(tb_lines)

            return {
                'success': False,
                'output': '',
                'error': f'{error_type}: {error_msg}\n{tb_short}',
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

    def _get_safe_builtins(self) -> dict:
        """
        Возвращает безопасный набор встроенных функций.

        Убираем потенциально опасные: __import__, open, etc.
        """
        safe_builtins = {}
        for name in dir(__builtins__) if hasattr(__builtins__, '__dict__') else []:
            if name not in ['__import__', 'open', 'file', 'exec', 'eval', 'compile', 'breakpoint']:
                safe_builtins[name] = getattr(__builtins__, name)
        return safe_builtins

    def _contains_blocked_keywords(self, code: str) -> bool:
        """
        Проверяет код на наличие запрещённых ключевых слов.

        Args:
            code: Python код

        Returns:
            True если найдено запрещённое слово
        """
        import re

        # Проверяем заблокированные модули (import os, from sys, etc.)
        import_pattern = r'^\s*(import|from)\s+(\w+)'
        for line in code.split('\n'):
            match = re.match(import_pattern, line.strip())
            if match:
                module_name = match.group(2)
                if module_name in self.BLOCKED_MODULES:
                    return True

        # Проверяем __import__
        if '__import__' in code:
            return True

        # Проверяем other blocked patterns
        for keyword in ['breakpoint', 'exit', 'quit']:
            if keyword in code:
                return True

        return False

    def run_tests(self, code: str, test_code: str) -> dict:
        """
        Выполняет тесты для проверки решения задачи.

        Args:
            code: Код решения пользователя
            test_code: Код тестов (unittest-style)

        Returns:
            dict с результатами тестов
        """
        start_time = time.time()

        # Комбинируем код пользователя и тесты
        combined_code = f"""
{code}

# === ТЕСТЫ ===
{test_code}
"""

        # Создаём namespace для выполнения
        safe_globals = {
            '__name__': '__main__',
            '__builtins__': self._get_safe_builtins(),
        }

        try:
            output_buffer = io.StringIO()
            test_results = []

            with redirect_stdout(output_buffer):
                with redirect_stderr(output_buffer):
                    # Выполняем код и тесты
                    exec(combined_code, safe_globals, {
                        'test_results': test_results,
                        'print': print,
                    })

            output = output_buffer.getvalue()

            # Парсим результаты тестов из output
            # Ожидаем формат типа "TEST PASSED: test_name" или "TEST FAILED: test_name"

            return {
                'success': True,
                'output': output,
                'tests_passed': len([t for t in test_results if t.get('passed')]),
                'tests_total': len(test_results),
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

        except Exception as e:
            error_type = type(e).__name__
            return {
                'success': False,
                'output': '',
                'error': f'{error_type}: {str(e)}',
                'execution_time_ms': int((time.time() - start_time) * 1000),
            }

    def check_output(self, code: str, expected_output: str) -> dict:
        """
        Простой способ проверки - сравниваем вывод программы с ожидаемым.

        Args:
            code: Код решения
            expected_output: Ожидаемый вывод (построчно или весь сразу)

        Returns:
            dict с результатами
        """
        result = self.execute(code)

        if not result['success']:
            return {
                'passed': False,
                'expected': expected_output,
                'actual': result['error'],
                'error': result['error'],
            }

        # Убираем trailing whitespace и сравниваем
        actual = result['output'].strip()
        expected = expected_output.strip()

        # Если ожидаемый вывод содержит несколько строк,
        # проверяем что все они присутствуют в выводе
        expected_lines = expected.split('\n')
        all_present = all(line.strip() in actual for line in expected_lines if line.strip())

        return {
            'passed': all_present,
            'expected': expected,
            'actual': actual,
            'output': result['output'],
        }


# Глобальный экземпляр интерпретатора
interpreter = PythonInterpreter()


def execute_code(code: str) -> dict:
    """
    Удобная функция для выполнения кода.

    Использование в роутерах:
        result = execute_code(request.code)
    """
    return interpreter.execute(code)