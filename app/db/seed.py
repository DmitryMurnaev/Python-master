"""
app/db/seed.py
==============
Заполнение базы данных начальными данными.

Этот модуль вызывается при старте приложения и создаёт:
- 8 блоков обучения с уроками
- Квизы к урокам
- Задачи для практики
- Карточки для повторения
"""

import json
from datetime import datetime, timezone

from app.db.session import AsyncSessionLocal
from app.models.learning import Block, Lesson, Quiz, Task
from app.models.flashcard import FlashCard
from app.models.user import User  # For reference
from app.services.gamification import create_default_achievements


# Контент для блоков обучения
BLOCKS_CONTENT = [
    {
        "id": 1,
        "title": "Основы Python",
        "description": "Переменные, типы данных, строки, списки, условия и циклы",
        "icon": "🐍",
        "min_level": 1,
        "xp_reward": 100,
        "lessons": [
            {
                "title": "Переменные и типы данных",
                "description": "Изучаем как хранить данные в переменных",
                "content": """
<h2>Переменные в Python</h2>
<p>Переменная — это именованная область памяти для хранения данных.</p>

<pre><code># Создание переменных
name = "Алексей"
age = 25
height = 1.75
is_student = True

print(name)  # Алексей
print(age)   # 25</code></pre>

<h3>Основные типы данных</h3>
<ul>
<li><b>str</b> — строка ("Hello")</li>
<li><b>int</b> — целое число (42)</li>
<li><b>float</b> — дробное число (3.14)</li>
<li><b>bool</b> — логический (True/False)</li>
</ul>

<h3>Проверка типа</h3>
<pre><code>x = 42
print(type(x))  # &lt;class 'int'&gt;

y = 3.14
print(type(y))  # &lt;class 'float'&gt;</code></pre>
                """,
                "quizzes": [
                    {
                        "title": "Переменные и типы данных",
                        "questions": [
                            {"question": "Какой тип данных у переменной x = 42?", "options": ["str", "int", "float", "bool"], "correct": 1},
                            {"question": "Что выведет print(type(3.14))?", "options": ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"], "correct": 1},
                            {"question": "Как создать переменную с дробным числом?", "options": ["x = 3.14", "x = float(3.14)", "x = 3,14", "Оба варианта A и B"], "correct": 3}
                        ]
                    }
                ],
                "tasks": [
                    {
                        "title": "Создайте переменные",
                        "description": "Создайте переменную name со значением 'Питон' и переменную version со значением 3. Выведите их через пробел.",
                        "starter_code": "# Создайте переменную name\n# Создайте переменную version\n\n# Выведите name и version через пробел\n",
                        "expected_output": "Питон 3",
                        "hints": ["Используйте print() с двумя аргументами через пробел"],
                        "xp_reward": 30
                    }
                ]
            },
            {
                "title": "Строки и операции с ними",
                "description": "Работа со строками в Python",
                "content": """
<h2>Строки в Python</h2>
<p>Строка — это последовательность символов. Строки неизменяемы.</p>

<pre><code># Конкатенация (склеивание)
greeting = "Привет, " + "мир!"  # "Привет, мир!"

# Верхний/нижний регистр
text = "Hello"
print(text.upper())   # HELLO
print(text.lower())   # hello

# Длина строки
print(len("Python"))   # 6

# Индексация
s = "Hello"
print(s[0])   # H
print(s[-1])  # o</code></pre>

<h3>f-строки (форматирование)</h3>
<pre><code>name = "Алексей"
age = 25
print(f"Меня зовут {name}, мне {age} лет")</code></pre>
                """,
                "quizzes": [],
                "tasks": [
                    {
                        "title": "Конкатенация строк",
                        "description": "Создайте две переменные first_name='Джон' и last_name='Смит', объедините их через пробел и выведите.",
                        "starter_code": "# Ваш код здесь\n",
                        "expected_output": "Джон Смит",
                        "hints": ["Используйте оператор + или f-строки"],
                        "xp_reward": 30
                    }
                ]
            },
            {
                "title": "Списки и основные операции",
                "description": "Создание и использование списков",
                "content": """
<h2>Списки</h2>
<p>Список — это упорядоченная коллекция элементов. Списки изменяемы.</p>

<pre><code># Создание списка
fruits = ["яблоко", "банан", "вишня"]

# Доступ по индексу
first = fruits[0]  # "яблоко"

# Изменение элемента
fruits[0] = "груша"

# Добавление элемента
fruits.append("слива")

# Удаление
fruits.remove("банан")

# Длина списка
print(len(fruits))</code></pre>

<h3>Срезы (slicing)</h3>
<pre><code>numbers = [0, 1, 2, 3, 4, 5]
print(numbers[1:4])   # [1, 2, 3]
print(numbers[:3])    # [0, 1, 2]
print(numbers[3:])    # [3, 4, 5]</code></pre>
                """,
                "quizzes": [],
                "tasks": [
                    {
                        "title": "Работа со списками",
                        "description": "Создайте список numbers = [1, 2, 3]. Добавьте туда число 4 и выведите длину списка.",
                        "starter_code": "# Создайте список numbers\n\n# Добавьте 4 и выведите длину\n",
                        "expected_output": "4",
                        "hints": ["Используйте append() и len()"],
                        "xp_reward": 30
                    }
                ]
            },
            {
                "title": "Условия if/else",
                "description": "Управление потоком программы",
                "content": """
<h2>Условные операторы</h2>
<p>Условия позволяют выполнять разный код в зависимости от условий.</p>

<pre><code>age = 18

if age >= 18:
    print("Взрослый")
elif age >= 12:
    print("Подросток")
else:
    print("Ребёнок")</code></pre>

<h3>Логические операторы</h3>
<pre><code># and - и
# or - или
# not - не

if age >= 18 and age < 65:
    print("Взрослый трудоспособный возраст")</code></pre>

<h3>Тернарный оператор</h3>
<pre><code>status = "взрослый" if age >= 18 else "ребёнок"</code></pre>
                """,
                "quizzes": [],
                "tasks": [
                    {
                        "title": "Условие",
                        "description": "Напишите программу которая проверяет число x=6 на чётность. Выведите 'чётное' или 'нечётное'.",
                        "starter_code": "x = 6\n# Ваш код здесь\n",
                        "expected_output": "чётное",
                        "hints": ["Используйте оператор % для проверки остатка от деления на 2"],
                        "xp_reward": 30
                    }
                ]
            },
            {
                "title": "Циклы for и while",
                "description": "Повторение действий в программе",
                "content": """
<h2>Циклы</h2>
<p>Циклы позволяют повторять блок кода несколько раз.</p>

<pre><code># Цикл for - перебор элементов
fruits = ["яблоко", "банан", "вишня"]
for fruit in fruits:
    print(fruit)

# Цикл for с range
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)

# Цикл while
count = 0
while count < 3:
    print(count)
    count += 1</code></pre>

<h3>Управление циклом</h3>
<pre><code># break - выход из цикла
for i in range(10):
    if i == 5:
        break
    print(i)

# continue - следующая итерация
for i in range(5):
    if i == 2:
        continue
    print(i)</code></pre>
                """,
                "quizzes": [],
                "tasks": [
                    {
                        "title": "Цикл for",
                        "description": "Выведите числа от 1 до 5 каждое на новой строке.",
                        "starter_code": "# Ваш код здесь\n",
                        "expected_output": "1\n2\n3\n4\n5",
                        "hints": ["Используйте range(1, 6)"],
                        "xp_reward": 30
                    }
                ]
            }
        ]
    },
    {
        "id": 2,
        "title": "Функции и модули",
        "description": "def, аргументы, lambda, область видимости, import",
        "icon": "⚙️",
        "min_level": 1,
        "xp_reward": 100,
        "lessons": [
            {
                "title": "Создание функций",
                "description": "Как определять и вызывать функции",
                "content": """
<h2>Функции</h2>
<p>Функция — это блок кода, который можно многократно вызывать.</p>

<pre><code># Определение функции
def greet(name):
    return f"Привет, {name}!"

# Вызов функции
message = greet("Алексей")
print(message)  # Привет, Алексей!

# Функция без аргументов
def say_hello():
    print("Привет!")

say_hello()</code></pre>

<h3>Return</h3>
<pre><code>def add(a, b):
    return a + b

result = add(3, 5)  # result = 8</code></pre>
                """,
                "quizzes": [],
                "tasks": [
                    {
                        "title": "Функция приветствие",
                        "description": "Создайте функцию greet которая принимает имя и возвращает 'Привет, {имя}!'.",
                        "starter_code": "# Создайте функцию greet\n\nprint(greet(\"Алексей\"))",
                        "expected_output": "Привет, Алексей!",
                        "hints": ["Используйте f-строку или конкатенацию"],
                        "xp_reward": 35
                    }
                ]
            },
            {
                "title": "Аргументы функций",
                "description": "Позиционные и именованные аргументы",
                "content": """
<h2>Аргументы функций</h2>
<pre><code># Аргументы по умолчанию
def greet(name, greeting="Привет"):
    return f"{greeting}, {name}!"

print(greet("Алексей"))  # Привет, Алексей!
print(greet("Алексей", "Здравствуйте"))  # Здравствуйте, Алексей!

# *args - произвольное количество аргументов
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3))  # 6

# **kwargs - произвольные именованные аргументы
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Алексей", age=25)</code></pre>
                """,
                "quizzes": [],
                "tasks": []
            }
        ]
    }
]


async def seed_initial_data(db: AsyncSessionLocal):
    """
    Заполняет базу данных начальным контентом.

    Вызывается при старте приложения если данные ещё не созданы.
    """
    # Проверяем есть ли уже данные
    from sqlalchemy import select, func
    result = await db.execute(select(func.count()).select_from(Block))
    count = result.scalar()

    if count > 0:
        print("Данные уже существуют, пропускаем seed")
        return

    print("Заполняем базу данных...")

    # Создаём блоки и уроки
    for block_data in BLOCKS_CONTENT:
        block = Block(
            id=block_data["id"],
            order_index=block_data["id"],
            title=block_data["title"],
            description=block_data["description"],
            icon=block_data["icon"],
            min_level=block_data["min_level"],
            xp_reward=block_data["xp_reward"],
        )
        db.add(block)

        # Создаём уроки
        for lesson_idx, lesson_data in enumerate(block_data["lessons"]):
            lesson = Lesson(
                block_id=block_data["id"],
                order_index=lesson_idx + 1,
                title=lesson_data["title"],
                description=lesson_data["description"],
                content=lesson_data["content"],
                xp_reward=30,
            )
            db.add(lesson)
            await db.flush()  # Получаем ID урока до создания связанных записей

            # Создаём квизы
            for quiz_data in lesson_data.get("quizzes", []):
                quiz = Quiz(
                    lesson_id=lesson.id,
                    title=quiz_data["title"],
                    questions=json.dumps(quiz_data["questions"]),
                    passing_score=70.0,
                )
                db.add(quiz)

            # Создаём задачи
            for task_idx, task_data in enumerate(lesson_data.get("tasks", [])):
                task = Task(
                    lesson_id=lesson.id,
                    order_index=task_idx + 1,
                    title=task_data["title"],
                    description=task_data["description"],
                    starter_code=task_data.get("starter_code"),
                    expected_output=task_data.get("expected_output"),
                    hints=json.dumps(task_data.get("hints", [])),
                    xp_reward=task_data.get("xp_reward", 30),
                )
                db.add(task)

    await db.commit()
    print("Начальные данные созданы!")


# Простой demo пользователь для тестирования
async def create_demo_user(db: AsyncSessionLocal):
    """Создаёт demo пользователя для тестирования."""
    from sqlalchemy import select
    from app.models.user import User

    result = await db.execute(select(User).where(User.email == "demo@example.com"))
    if result.scalar_one_or_none():
        return

    from app.core.security import get_password_hash

    demo_user = User(
        username="demo",
        email="demo@example.com",
        hashed_password=get_password_hash("demo123"),
        xp=150,
        level=2,
        streak_days=3,
    )
    db.add(demo_user)
    await db.commit()
    print("Demo пользователь создан: demo@example.com / demo123")