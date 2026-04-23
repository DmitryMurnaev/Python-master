-- Seed data for Python Master
-- Creates all 8 blocks with lessons, quizzes, tasks, and flashcards

-- Block 1: Python Basics
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(1, 1, 'Основы Python', 'Переменные, типы данных, строки, списки, условия и циклы', '🐍', 1, 100);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(1, 1, 1, 'Переменные и типы данных', 'Изучаем как хранить данные в переменных', '<h2>Переменные в Python</h2><p>Переменная — это именованная область памяти для хранения данных.</p><pre><code># Создание переменных
name = "Алексей"
age = 25
height = 1.75
is_student = True

print(name)  # Алексей
print(age)   # 25</code></pre><h3>Основные типы данных</h3><ul><li><b>str</b> — строка ("Hello")</li><li><b>int</b> — целое число (42)</li><li><b>float</b> — дробное число (3.14)</li><li><b>bool</b> — логический (True/False)</li></ul>', 0, 30),
(2, 1, 2, 'Строки и операции с ними', 'Работа со строками в Python', '<h2>Строки в Python</h2><p>Строка — это последовательность символов.</p><pre><code># Конкатенация
greeting = "Привет, " + "мир!"  # "Привет, мир!"

# Верхний регистр
text = "hello".upper()  # "HELLO"

# Длина строки
length = len("Python")  # 6</code></pre>', 0, 30),
(3, 1, 3, 'Списки и основные операции', 'Создание и использование списков', '<h2>Списки</h2><p>Список — это упорядоченная коллекция элементов.</p><pre><code># Создание списка
fruits = ["яблоко", "банан", "вишня"]

# Доступ по индексу
first = fruits[0]  # "яблоко"

# Добавление элемента
fruits.append("груша")</code></pre>', 0, 30),
(4, 1, 4, 'Условия if/else', 'Управление потоком программы', '<h2>Условные операторы</h2><pre><code>age = 18

if age >= 18:
    print("Взрослый")
elif age >= 12:
    print("Подросток")
else:
    print("Ребёнок")</code></pre>', 0, 30),
(5, 1, 5, 'Циклы for и while', 'Повторение действий в программе', '<h2>Циклы</h2><pre><code># Цикл for
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# Цикл while
count = 0
while count < 3:
    print(count)
    count += 1</code></pre>', 0, 30),
(6, 1, 6, 'Проект: Калькулятор', 'Создаём простой калькулятор', 'Создайте калькулятор, который принимает два числа и операцию (+, -, *, /) и выводит результат.', 1, 50);

-- Block 2: Functions and Modules
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(2, 2, 'Функции и модули', 'def, аргументы, lambda, область видимости, import', '⚙️', 1, 100);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(7, 2, 1, 'Создание функций', 'Как определять и вызывать функции', '<h2>Функции</h2><pre><code>def greet(name):
    return f"Привет, {name}!"

message = greet("Алексей")
print(message)  # Привет, Алексей!</code></pre>', 0, 30),
(8, 2, 2, 'Аргументы функций', 'Позиционные и именованные аргументы', '<h2>Аргументы</h2><pre><code># Аргументы по умолчанию
def greet(name, greeting="Привет"):
    return f"{greeting}, {name}!"

# Именованные аргументы
greet(name="Алексей", greeting="Здравствуйте")</code></pre>', 0, 30),
(9, 2, 3, 'Lambda функции', 'Анонимные функции', '<h2>Lambda</h2><pre><code># Lambda - короткая функция
square = lambda x: x ** 2
print(square(5))  # 25

# Сортировка с lambda
pairs = [(1, "один"), (3, "три"), (2, "два")]
pairs.sort(key=lambda p: p[0])</code></pre>', 0, 30),
(10, 2, 4, 'Область видимости', 'Глобальные и локальные переменные', '<h2>Область видимости</h2><pre><code>x = "глобальная"

def func():
    x = "локальная"  # Новая локальная переменная
    global y  # Изменяем глобальную
    y = 100</code></pre>', 0, 30),
(11, 2, 5, 'Модули и import', 'Использование готовых модулей', '<h2>Модули</h2><pre><code>import math
print(math.sqrt(16))  # 4.0

from datetime import datetime
now = datetime.now()</code></pre>', 0, 30),
(12, 2, 6, 'Проект: Игра "Угадай число"', 'Создаём игру с функциями', 'Создайте игру "Угадай число" с подсчётом попыток.', 1, 50);

-- Block 3: Collections
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(3, 3, 'Коллекции', 'Словари, множества, кортежи, list comprehensions, генераторы', '📊', 2, 100);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(13, 3, 1, 'Словари (dict)', 'Работа с ключ-значение', '<h2>Словари</h2><pre><code>person = {"name": "Алексей", "age": 25}
print(person["name"])  # Алексей

# Добавление
person["city"] = "Москва"

# Методы
print(person.keys())
print(person.values())</code></pre>', 0, 30),
(14, 3, 2, 'Множества (set)', 'Уникальные элементы', '<h2>Множества</h2><pre><code>fruits = {"яблоко", "банан", "яблоко"}
print(fruits)  # {"яблоко", "банан"}

# Операции
a = {1, 2, 3}
b = {2, 3, 4}
print(a | b)  # объединение
print(a & b)  # пересечение</code></pre>', 0, 30),
(15, 3, 3, 'Кортежи (tuple)', 'Неизменяемые последовательности', '<h2>Кортежи</h2><pre><code>point = (10, 20)
x, y = point  # распаковка

# Кортеж нельзя изменить
point[0] = 15  # Ошибка!</code></pre>', 0, 30),
(16, 3, 4, 'List comprehensions', 'Генерация списков', '<h2>List Comprehensions</h2><pre><code># Генерация списка
squares = [x**2 for x in range(5)]
# [0, 1, 4, 9, 16]

# С условием
even = [x for x in range(10) if x % 2 == 0]</code></pre>', 0, 30),
(17, 3, 5, 'Генераторы', 'Ленивые коллекции', '<h2>Генераторы</h2><pre><code>def count_up_to(n):
    i = 0
    while i < n:
        yield i
        i += 1

for num in count_up_to(3):
    print(num)  # 0, 1, 2</code></pre>', 0, 30),
(18, 3, 6, 'Проект: Анализатор текста', 'Подсчёт статистики текста', 'Создайте программу для анализа текста: подсчёт слов, символов, частотности.', 1, 50);

-- Block 4: Files and Exceptions
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(4, 4, 'Файлы и исключения', 'open, try/except, with', '📁', 2, 100);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(19, 4, 1, 'Работа с файлами', 'Чтение и запись файлов', '<h2>Файлы</h2><pre><code># Запись в файл
with open("file.txt", "w") as f:
    f.write("Hello!")

# Чтение из файла
with open("file.txt", "r") as f:
    content = f.read()</code></pre>', 0, 30),
(20, 4, 2, 'Обработка исключений', 'try/except/finally', '<h2>Исключения</h2><pre><code>try:
    result = 10 / 0
except ZeroDivisionError:
    print("На ноль делить нельзя!")
except Exception as e:
    print(f"Ошибка: {e}")
finally:
    print("Выполняется всегда")</code></pre>', 0, 30),
(21, 4, 3, 'Контекстные менеджеры', 'with и менеджмент ресурсов', '<h2>Контекстные менеджеры</h2><pre><code># with автоматически закрывает файл
with open("data.txt") as f:
    data = f.read()
# файл закрыт

# Свои менеджеры
class MyResource:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        cleanup()</code></pre>', 0, 30),
(22, 4, 4, 'Проект: Заметки', 'Создаём приложение для заметок', 'Создайте приложение заметок с сохранением в файл.', 1, 50);

-- Block 5: OOP
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(5, 5, 'Объектно-ориентированное программирование', 'Классы, наследование, полиморфизм, магические методы', '🏗️', 3, 150);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(23, 5, 1, 'Классы и объекты', 'Создание классов', '<h2>Классы</h2><pre><code>class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} говорит: Гав!"

my_dog = Dog("Бобик", 3)
print(my_dog.bark())</code></pre>', 0, 30),
(24, 5, 2, 'Наследование', 'Наследование и полиморфизм', '<h2>Наследование</h2><pre><code>class Animal:
    def speak(self):
        pass

class Cat(Animal):
    def speak(self):
        return "Мяу!"

class Dog(Animal):
    def speak(self):
        return "Гав!"</code></pre>', 0, 30),
(25, 5, 3, 'Магические методы', '__str__, __len__, __iter__', '<h2>Магические методы</h2><pre><code>class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)</code></pre>', 0, 30),
(26, 5, 4, 'Проект: Система управления студентами', 'Создаём классы для студентов и курсов', 'Создайте систему управления студентами с классами Student, Course, Group.', 1, 60);

-- Block 6: Advanced
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(6, 6, 'Продвинутые темы', 'Декораторы, итераторы, контекстные менеджеры, типизация', '🚀', 4, 150);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(27, 6, 1, 'Декораторы', 'Создание и использование декораторов', '<h2>Декораторы</h2><pre><code>def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("До вызова")
        result = func(*args, **kwargs)
        print("После вызова")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Привет!")</code></pre>', 0, 40),
(28, 6, 2, 'Итераторы и генераторы', 'Создание своих итераторов', '<h2>Итераторы</h2><pre><code>class Counter:
    def __init__(self, limit):
        self.current = 0
        self.limit = limit

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        self.current += 1
        return self.current - 1

for num in Counter(3):
    print(num)  # 0, 1, 2</code></pre>', 0, 40),
(29, 6, 3, 'Типизация', 'Аннотации типов в Python', '<h2>Type Hints</h2><pre><code>from typing import List, Optional

def greet(name: str) -> str:
    return f"Привет, {name}!"

def process(items: List[int]) -> Optional[int]:
    return items[0] if items else None</code></pre>', 0, 40),
(30, 6, 4, 'Проект: Логирующий декоратор', 'Создаём систему логирования', 'Создайте декоратор для логирования вызовов функций.', 1, 60);

-- Block 7: Databases
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(7, 7, 'Основы баз данных', 'SQLite, SQLAlchemy, работа с БД из Python', '🗄️', 5, 150);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(31, 7, 1, 'Введение в SQL', 'Основы SQL запросов', '<h2>SQL</h2><pre><code>-- Создание таблицы
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);

-- Вставка
INSERT INTO users (name) VALUES ("Алексей");

-- Выборка
SELECT * FROM users WHERE id = 1;</code></pre>', 0, 40),
(32, 7, 2, 'SQLite в Python', 'Использование sqlite3', '<h2>sqlite3</h2><pre><code>import sqlite3

conn = sqlite3.connect("mydb.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Алексей",))
conn.commit()</code></pre>', 0, 40),
(33, 7, 3, 'SQLAlchemy ORM', 'Объектно-реляционное отображение', '<h2>SQLAlchemy</h2><pre><code>from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)</code></pre>', 0, 40),
(34, 7, 4, 'Проект: ToDo приложение с БД', 'Создаём ToDo с сохранением в SQLite', 'Создайте ToDo приложение с хранением данных в SQLite.', 1, 80);

-- Block 8: FastAPI
INSERT INTO blocks (id, order_index, title, description, icon, min_level, xp_reward) VALUES
(8, 8, 'Введение в FastAPI', 'Основы FastAPI для создания веб-приложений', '⚡', 6, 100);

INSERT INTO lessons (id, block_id, order_index, title, description, content, is_project, xp_reward) VALUES
(35, 8, 1, 'Первое приложение FastAPI', 'Создаём простой API', '<h2>Hello FastAPI</h2><pre><code>from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}</code></pre>', 0, 40),
(36, 8, 2, 'Маршруты и запросы', 'GET, POST, параметры', '<h2>Маршруты</h2><pre><code>from fastapi import FastAPI, Query

app = FastAPI()

@app.post("/items/")
def create_item(name: str, price: float):
    return {"name": name, "price": price}

@app.get("/search")
def search(q: str = Query(default=None)):
    return {"query": q}</code></pre>', 0, 40),
(37, 8, 3, 'Проект: REST API для заметок', 'Создаём API для CRUD операций', 'Создайте REST API для заметок с полным CRUD.', 1, 80);
"""

-- Quiz questions
INSERT INTO quizzes (id, lesson_id, title, questions) VALUES
(1, 1, 'Переменные и типы данных', '[{"question": "Какой тип данных у переменной x = 42?", "options": ["str", "int", "float", "bool"], "correct": 1}, {"question": "Что выведет print(type(3.14))?", "options": ["<class ''int''>", "<class ''float''>", "<class ''str''>", "<class ''double''>"], "correct": 1}, {"question": "Как создать переменную с дробным числом?", "options": ["x = 3.14", "x = float(3.14)", "x = 3,14", "Оба варианта A и B"], "correct": 3}]'),
(2, 2, 'Строки', '[{"question": "Какой метод делает строку заглавной?", "options": ["upper()", "capitalize()", "uppercase()", "big()"], "correct": 0}, {"question": "Как объединить строки ''Hello'' и ''World''?", "options": ["''Hello'' + ''World''", "''Hello''.concat(''World'')", "''Hello'' & ''World''", "concat(''Hello'', ''World'')"], "correct": 0}, {"question": "Что вернёт len(''Python'')?", "options": ["5", "6", "7", "Error"], "correct": 1}]'),
(3, 3, 'Списки', '[{"question": "Как добавить элемент в конец списка?", "options": ["list.add()", "list.append()", "list.push()", "list.insert()"], "correct": 1}, {"question": "Что вернёт [1,2,3][-1]?", "options": ["1", "2", "3", "Error"], "correct": 2}, {"question": "Как получить первые 2 элемента списка?", "options": ["list[0:2]", "list[:2]", "list[0:1]", "Оба варианта A и B"], "correct": 3}]'),
(4, 4, 'Условия', '[{"question": "Какой результат: if True: print(''yes'') else: print(''no'')?", "options": ["yes", "no", "Error", "yes no"], "correct": 0}, {"question": "elif это?", "options": ["Ключевое слово", "Функция", "Метод", "Оператор"], "correct": 0}, {"question": "Что делает оператор ==?", "options": ["Присваивает значение", "Сравнивает на равенство", "Проверяет тип", "Ничего"], "correct": 1}]'),
(5, 5, 'Циклы', '[{"question": "Сколько раз выполнится for i in range(3)?", "options": ["2", "3", "4", "1"], "correct": 1}, {"question": "Как остановить бесконечный цикл while?", "options": ["break", "exit()", "stop()", "Оба варианта A"], "correct": 0}, {"question": "Что делает continue в цикле?", "options": ["Выходит из цикла", "Переходит к следующей итерации", "Останавливает программу", "Ничего"], "correct": 1}]'),
(6, 7, 'Функции', '[{"question": "Как объявить функцию?", "options": ["function myFunc():", "def myFunc():", "func myFunc()", "declare myFunc()"], "correct": 1}, {"question": "Что делает return?", "options": ["Выводит значение", "Возвращает значение из функции", "Завершает программу", "Объявляет переменную"], "correct": 1}, {"question": "Какой символ разделяет аргументы функции?", "options": [";", ":", ",", "."], "correct": 2}]'),
(7, 13, 'Словари', '[{"question": "Как получить значение по ключу?", "options": ["dict.get(key)", "dict[key]", "Оба варианта", "Ни один"], "correct": 2}, {"question": "Как добавить новую пару?", "options": ["dict.add(key, value)", "dict[key] = value", "dict.append(key, value)", "dict.push(key, value)"], "correct": 1}, {"question": "Что вернёт {1: ''a'', 2: ''b''}.get(3)?", "options": ["3", "''b''", "None", "Error"], "correct": 2}]'),
(8, 23, 'Классы', '[{"question": "Как создать объект класса Dog?", "options": ["dog = new Dog()", "dog = Dog()", "dog = create Dog()", "dog = Dog.new()"], "correct": 1}, {"question": "Что такое __init__?", "options": ["Деструктор", "Конструктор", "Метод удаления", "Атрибут"], "correct": 1}, {"question": "self это?", "options": ["Ключевое слово", "Ссылка на текущий объект", "Атрибут класса", "Метод"], "correct": 1}]');

-- Tasks
INSERT INTO tasks (id, lesson_id, order_index, title, description, starter_code, expected_output, hints, xp_reward) VALUES
(1, 1, 1, 'Создайте переменные', 'Создайте переменную name со значением "Питон" и переменную version со значением 3. Выведите их через пробел.', '# Создайте переменную name\n# Создайте переменную version\n\n# Выведите name и version через пробел\n', 'Питон 3', '["Используйте print() с двумя аргументами"]', 30),
(2, 2, 1, 'Конкатенация строк', 'Создайте две переменных first_name и last_name, объедините их через пробел и выведите результат.', '# Ваш код здесь\n', 'Джон Смит', '["Используйте оператор + или f-строки"]', 30),
(3, 3, 1, 'Работа со списками', 'Создайте список numbers = [1, 2, 3]. Добавьте туда число 4 и выведите длину списка.', '# Создайте список numbers\n\n# Добавьте 4 и выведите длину\n', '4', '["Используйте append() и len()"]', 30),
(4, 4, 1, 'Условие', 'Напишите программу которая проверяет число x на чётность. Если чётное - выведите "чётное", если нечётное - "нечётное".', 'x = 6\n# Ваш код здесь\n', 'чётное', '["Используйте оператор % для проверки остатка"]', 30),
(5, 5, 1, 'Цикл for', 'Выведите числа от 1 до 5 каждое на новой строке.', '# Ваш код здесь\n', '1\n2\n3\n4\n5', '["Используйте range(1, 6)"]', 30),
(6, 7, 1, 'Функция приветствие', 'Создайте функцию greet которая принимает имя и возвращает "Привет, {имя}!".', '# Создайте функцию greet\n\nprint(greet("Алексей"))', 'Привет, Алексей!', '["Используйте f-строку или конкатенацию"]', 35),
(7, 13, 1, 'Словарь пользователя', 'Создайте словарь user с ключами name и age. Выведите значение по ключу name.', 'user = {}\n# Добавьте name="Алексей" и age=25\n\nprint(user["name"])', 'Алексей', '["Используйте словарь[key] = value"]', 35),
(8, 23, 1, 'Простой класс', 'Создайте класс Cat с конструктором принимающим name и методом meow() возвращающим "{name} говорит Мяу!".', '# Создайте класс Cat\n\ncat = Cat("Барсик")\nprint(cat.meow())', 'Барсик говорит Мяу!', '["Не забудьте про __init__ и self"]', 40),
(9, 27, 1, 'Простой декоратор', 'Создайте декоратор uppercase который делает возвращаемое значение функции заглавными.', 'def uppercase(func):\n    # Ваш код здесь\n    pass\n\n@uppercase\ndef greet():\n    return "привет"\n\nprint(greet())', 'ПРИВЕТ', '["Декоратор должен возвращать функцию-обёртку"]', 45),
(10, 31, 1, 'Подсчёт слов', 'Напишите функцию count_words которая принимает строку и возвращает количество слов (разделенных пробелами).', 'def count_words(text):\n    # Ваш код\n    pass\n\nprint(count_words("раз два три"))', '3', '["Используйте split()"]', 35);

-- Flashcards (one set for each block)
INSERT INTO flashcards (user_id, block_id, question, answer, next_review_date) VALUES
(0, 1, 'Что такое переменная?', 'Именованная область памяти для хранения данных'),
(0, 1, 'Назовите 4 основных типа данных в Python', 'str, int, float, bool'),
(0, 1, 'Как создать список?', 'numbers = [1, 2, 3]'),
(0, 1, 'Как обратиться к элементу списка?', 'list[index] - индексация начинается с 0'),
(0, 1, 'Что делает оператор %?', 'Возвращает остаток от деления'),
(0, 2, 'Как объявить функцию?', 'def function_name(parameters):'),
(0, 2, 'Что делает return?', 'Возвращает значение из функции'),
(0, 2, 'Что такое lambda?', 'Анонимная (безымянная) функция)'),
(0, 2, 'Как импортировать модуль?', 'import module_name'),
(0, 2, 'Что означает *args?', 'Произвольное количество позиционных аргументов'),
(0, 3, 'Чем отличается dict от list?', 'dict хранит пары ключ-значение, list - упорядоченные элементы'),
(0, 3, 'Что такое set?', 'Множество - коллекция уникальных элементов'),
(0, 3, 'Что такое tuple?', 'Неизменяемая последовательность элементов'),
(0, 3, 'Что вернёт [x for x in range(5) if x%2==0]?', '[0, 2, 4] - чётные числа'),
(0, 4, 'Что делает with open()?', 'Контекстный менеджер - автоматически закрывает файл'),
(0, 4, 'Как обработать исключение?', 'try: ... except ExceptionType: ...'),
(0, 4, 'Что такое finally?', 'Блок выполняется всегда - и при исключении, и без'),
(0, 5, 'Что такое класс?', 'Шаблон для создания объектов с атрибутами и методами'),
(0, 5, 'Что делает __init__?', 'Конструктор - вызывается при создании объекта'),
(0, 5, 'Что такое наследование?', 'Возможность создать класс на основе другого'),
(0, 6, 'Что такое декоратор?', 'Функция которая модифицирует поведение другой функции'),
(0, 6, 'Что такое итератор?', 'Объект который позволяет перебирать элементы коллекции'),
(0, 6, 'Зачем нужны type hints?', 'Для документирования и проверки типов данных'),
(0, 7, 'Что такое SQL?', 'Язык структурированных запросов для работы с БД'),
(0, 7, 'Что делает SELECT?', 'Выбирает данные из таблицы'),
(0, 8, 'Что такое API?', 'Application Programming Interface - способ взаимодействия программ');