"""
app/api/tasks.py
================
Роутер для задач - проверка решений через интерпретатор.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.learning import Task, Lesson
from app.models.progress import TaskSubmission, UserProgress
from app.core.security import get_current_user
from app.schemas.learning import TaskSubmissionCode, TaskSubmissionResult
from app.services.interpreter import interpreter
from app.services.gamification import update_user_xp, XP_REWARDS, check_achievements

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о задаче.

    Args:
        task_id: ID задачи
    """
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options()
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Получаем историю попыток
    result = await db.execute(
        select(TaskSubmission)
        .where(TaskSubmission.user_id == current_user.id)
        .where(TaskSubmission.task_id == task_id)
        .order_by(TaskSubmission.created_at.desc())
        .limit(5)
    )
    recent_submissions = result.scalars().all()

    return {
        'id': task.id,
        'lesson_id': task.lesson_id,
        'title': task.title,
        'description': task.description,
        'starter_code': task.starter_code or '',
        'hints': task.hints_list if hasattr(task, 'hints_list') else [],
        'expected_output': task.expected_output,
        'xp_reward': task.xp_reward,
        'recent_submissions': [
            {
                'id': s.id,
                'result': s.result,
                'created_at': s.created_at,
                'output': s.output,
            }
            for s in recent_submissions
        ],
    }


@router.post("/{task_id}/submit")
async def submit_task(
    task_id: int,
    submission: TaskSubmissionCode,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Проверить решение задачи.

    Логика проверки:
    1. Если у задачи есть test_code - запускаем тесты
    2. Если есть expected_output - сравниваем вывод
    3. Иначе просто выполняем код и смотрим что получилось

    Args:
        task_id: ID задачи
        submission: Код решения
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Запускаем код через интерпретатор
    if task.test_code:
        # Используем систему тестов
        test_result = interpreter.run_tests(submission.code, task.test_code)

        if test_result['success']:
            tests_passed = test_result.get('tests_passed', 0)
            tests_total = test_result.get('tests_total', 0)

            # Считаем результат PASSED только если все тесты прошли
            result_status = 'PASS' if tests_passed == tests_total else 'FAIL'

            # Сохраняем попытку
            task_submission = TaskSubmission(
                user_id=current_user.id,
                task_id=task_id,
                code=submission.code,
                result=result_status,
                output=test_result.get('output', ''),
                tests_passed=tests_passed,
                tests_total=tests_total,
                execution_time_ms=test_result.get('execution_time_ms'),
            )
            db.add(task_submission)
            await db.commit()

            # Если задача решена правильно - начисляем XP
            xp_earned = 0
            is_final = False

            if result_status == 'PASS':
                # Проверяем что это первое успешное решение
                result = await db.execute(
                    select(TaskSubmission)
                    .where(TaskSubmission.user_id == current_user.id)
                    .where(TaskSubmission.task_id == task_id)
                    .where(TaskSubmission.result == 'PASS')
                    .order_by(TaskSubmission.created_at.asc())
                    .limit(1)
                )
                first_success = result.scalar_one_or_none()

                if first_success and first_success.id == task_submission.id:
                    # Первое успешное решение
                    xp_earned = task.xp_reward
                    await update_user_xp(db, current_user, xp_earned, f"Решение задачи: {task.title}")
                    is_final = True

                # Обновляем прогресс по уроку
                await _update_lesson_progress(db, current_user, task.lesson_id)

                # Проверяем достижения
                await check_achievements(db, current_user)

            return TaskSubmissionResult(
                result=result_status,
                output=test_result.get('output', ''),
                error_message=test_result.get('error'),
                tests_passed=tests_passed,
                tests_total=tests_total,
                xp_earned=xp_earned,
                is_final=is_final,
            )
        else:
            # Ошибка выполнения
            task_submission = TaskSubmission(
                user_id=current_user.id,
                task_id=task_id,
                code=submission.code,
                result='ERROR',
                error_message=test_result.get('error'),
                execution_time_ms=test_result.get('execution_time_ms'),
            )
            db.add(task_submission)
            await db.commit()

            return TaskSubmissionResult(
                result='ERROR',
                error_message=test_result.get('error'),
                tests_passed=0,
                tests_total=test_result.get('tests_total', 0),
                xp_earned=0,
                is_final=False,
            )

    elif task.expected_output:
        # Простое сравнение вывода
        check_result = interpreter.check_output(submission.code, task.expected_output)

        if check_result['passed']:
            result_status = 'PASS'
        else:
            result_status = 'FAIL'

        task_submission = TaskSubmission(
            user_id=current_user.id,
            task_id=task_id,
            code=submission.code,
            result=result_status,
            output=check_result.get('output', ''),
            error_message=None if check_result['passed'] else f"Ожидалось: {check_result['expected']}",
        )
        db.add(task_submission)
        await db.commit()

        xp_earned = 0
        is_final = False

        if result_status == 'PASS':
            xp_earned = task.xp_reward
            await update_user_xp(db, current_user, xp_earned, f"Решение задачи: {task.title}")
            await _update_lesson_progress(db, current_user, task.lesson_id)
            await check_achievements(db, current_user)
            is_final = True

        return TaskSubmissionResult(
            result=result_status,
            output=check_result.get('output', ''),
            error_message=check_result.get('error'),
            xp_earned=xp_earned,
            is_final=is_final,
        )

    else:
        # Просто выполняем код
        exec_result = interpreter.execute(submission.code)

        if exec_result['success']:
            task_submission = TaskSubmission(
                user_id=current_user.id,
                task_id=task_id,
                code=submission.code,
                result='PASS',  # Для открытых задач всегда PASS
                output=exec_result['output'],
                execution_time_ms=exec_result['execution_time_ms'],
            )
            db.add(task_submission)
            await db.commit()

            # Для открытых задач даём XP просто за выполнение
            xp_earned = 0
            if exec_result['output'].strip():  # Есть вывод
                xp_earned = task.xp_reward // 2  # Половина XP
                await update_user_xp(db, current_user, xp_earned, f"Выполнение задачи: {task.title}")
                is_final = True
            else:
                is_final = False

            return TaskSubmissionResult(
                result='PASS',
                output=exec_result['output'],
                xp_earned=xp_earned,
                is_final=is_final,
            )
        else:
            task_submission = TaskSubmission(
                user_id=current_user.id,
                task_id=task_id,
                code=submission.code,
                result='ERROR',
                error_message=exec_result['error'],
                execution_time_ms=exec_result['execution_time_ms'],
            )
            db.add(task_submission)
            await db.commit()

            return TaskSubmissionResult(
                result='ERROR',
                error_message=exec_result['error'],
                xp_earned=0,
                is_final=False,
            )


@router.post("/{task_id}/run")
async def run_code(
    task_id: int,
    submission: TaskSubmissionCode,
    db: AsyncSession = Depends(get_db)
):
    """
    Просто выполнить код без проверки (кнопка "Запустить").

    Используется для интерактивного режима когда пользователь
    хочет просто проверить свой код.

    Args:
        task_id: ID задачи (для подстановки starter_code если нужно)
        submission: Код для выполнения
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    # Выполняем код
    exec_result = interpreter.execute(submission.code)

    return {
        'success': exec_result['success'],
        'output': exec_result['output'],
        'error': exec_result['error'],
        'execution_time_ms': exec_result['execution_time_ms'],
    }


async def _update_lesson_progress(
    db: AsyncSession,
    user: User,
    lesson_id: int
):
    """
    Обновляет прогресс урока после успешного решения задачи.

    Если все обязательные задачи урока решены - урок считается пройденным.
    """
    from datetime import datetime, timezone

    # Получаем все задачи урока
    result = await db.execute(
        select(Task).where(Task.lesson_id == lesson_id)
    )
    tasks = result.scalars().all()

    if not tasks:
        return

    # Получаем все решённые задачи пользователя для этого урока
    result = await db.execute(
        select(TaskSubmission)
        .where(TaskSubmission.user_id == user.id)
        .where(TaskSubmission.result == 'PASS')
        .where(TaskSubmission.task_id.in_([t.id for t in tasks]))
    )
    solved_task_ids = {sub.task_id for sub in result.scalars().all()}

    # Проверяем что все задачи решены
    all_solved = all(task.id in solved_task_ids for task in tasks)

    # Обновляем или создаём прогресс
    result = await db.execute(
        select(UserProgress)
        .where(UserProgress.user_id == user.id)
        .where(UserProgress.lesson_id == lesson_id)
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            lesson_id=lesson_id,
        )
        db.add(progress)

    if all_solved and not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = datetime.now(timezone.utc)

        # Добавляем XP за завершение урока
        await update_user_xp(db, user, XP_REWARDS['lesson_completed'], "Завершение урока")

    await db.commit()