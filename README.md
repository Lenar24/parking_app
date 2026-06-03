# 🅿️ Парковочный сервис

Автоматическая система оплаты парковки с веб-интерфейсом и REST API.
___

## 📋 Описание проекта

Сервис позволяет:
- Регистрировать клиентов с банковскими картами
- Управлять парковками (добавление, просмотр)
- Осуществлять заезд и выезд автомобилей
- Автоматически рассчитывать стоимость парковки (2 руб/мин)
- Просматривать историю парковок клиентов

## 🛠 Технологии

- **Flask** - веб-фреймворк
- **Flask-SQLAlchemy** - ORM для работы с БД
- **SQLite** - база данных
- **pytest** - тестирование
- **Factory Boy + Faker** - генерация тестовых данных

## 🔧 Инструменты

- **Black** — форматирование кода
- **Isort** — сортировка импортов
- **Flake8** — проверка стиля кода
- **Mypy** — проверка типов

## 📁 Структура проекта

```
parking_app/
├── app/                          # Основной код приложения
│   ├── __init__.py               # Фабрика приложения
│   ├── config.py                 # Конфигурация
│   ├── models.py                 # ORM-модели
│   ├── api/                      # API эндпоинты
│   │   ├── __init__.py
│   │   ├── clients.py
│   │   ├── parkings.py
│   │   └── client_parkings.py
│   └── templates/                # HTML шаблоны
│       ├── index.html
│       ├── clients.html
│       ├── parkings.html
│       ├── parking_operations.html
│       └── client_history.html
│
├── tests/                        # Тесты
│   ├── __init__.py
│   ├── conftest.py               # Фикстуры pytest
│   ├── factories.py              # Фабрики для тестов
│   ├── test_clients_api.py
│   ├── test_parkings_api.py
│   ├── test_client_parkings_api.py
│   ├── test_models.py
│   └── test_factories.py
│
├── instance/                     # База данных (создается автоматически)
│   └── parking.db                # SQLite база данных
│
├── .venv/                        # Виртуальное окружение (игнорируется)
│
├── .gitignore                    # Git игнорируемые файлы
├── .gitlab-ci.yml                # GitLab CI/CD конфигурация
├── .flake8                       # Flake8 конфигурация
├── pyproject.toml                # Black, Isort, Mypy конфигурация
├── .pre-commit-config.yaml       # Pre-commit хуки
├── requirements.txt              # Зависимости проекта
├── pytest.ini                    # Настройки pytest
├── main.py                       # Точка входа
└── README.md                     # Документация проекта
```

## 🚀 Быстрый старт

```
# Скопируйте проект в нужную директорию
cd ~/PycharmProjects/python_advanced/module_29_testing/parking_app

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установите зависимости
pip install -r requirements.txt

# Инициализация базы данных
flask init-db

# (Опционально) Заполнение БД тестовыми данными
flask seed-data

# Запуск приложения через Flask CLI
flask run

# Запуск приложения напрямую
python main.py
```

### Приложение будет доступно по адресу: http://localhost:5000

### 🌐 Веб-интерфейс:

| Страница    | URL           | Описание                      |
|-------------|---------------|-------------------------------|
| Главная     | `/`           | Статистика и быстрые действия |
| Клиенты     | `/clients`    | Управление клиентами          |
| Парковки    | `/parkings`   | Управление парковками         |
| Заезд/Выезд | `/operations` | Операции парковки             |
| История     | `/history`    | История парковок клиента      |

### 📡 API Endpoints

#### Клиенты:

| Метод | URL                 | Описание             |
|-------|---------------------|----------------------|
| GET   | `/api/clients`      | Список всех клиентов |
| GET   | `/api/clients/{id}` | Информация о клиенте |
| POST  | `/api/clients`      | Создание клиента     |

#### Парковки:

| Метод | URL             | Описание             |
|-------|-----------------|----------------------|
| GET   | `/api/parkings` | Список всех парковок |
| POST  | `/api/parkings` | Создание парковки    |

#### Операции парковки:

| Метод  | URL                                | Описание          |
|--------|------------------------------------|-------------------|
| POST   | `/api/client_parkings`             | Заезд на парковку |
| DELETE | `/api/client_parkings`             | Выезд с парковки  |
| GET    | `/api/client_parkings/active`      | Активные сессии   |
| GET    | `/api/client_parkings/client/{id}` | История клиента   |

## 🧪 Тестирование

```
# Запуск всех тестов
pytest -v

# Запуск с отчетом о покрытии
pytest --cov=app --cov-report=term tests/

# Запуск конкретных тестов:

# Только тесты клиентов
pytest tests/test_clients_api.py -v

# Только тесты с маркером parking (заезд/выезд)
pytest -m parking -v

# Только тесты фабрик
pytest tests/test_factories.py -v
```

### Ожидаемый результат тестов

```
=================== 31 passed in 0.85s =========================
```

## 📝 Проверка с линтерами

```
# Форматирование
black .
isort --profile black .

# Проверки
black --check .
isort --check-only --profile black .
flake8 .
mypy . --ignore-missing-imports
```

## 📊 Проверка API через curl

```
# 1. Создать клиента
curl -X POST http://localhost:5000/api/clients \
  -H "Content-Type: application/json" \
  -d '{"name":"Иван","surname":"Петров","credit_card":"1234-5678-9012-3456","car_number":"A123BC77"}' \
  | python -m json.tool

# 2. Создать парковку
curl -X POST http://localhost:5000/api/parkings \
  -H "Content-Type: application/json" \
  -d '{"address":"ул. Ленина, 10","opened":true,"count_places":50}' \
  | python -m json.tool

# 3. Заехать на парковку
curl -X POST http://localhost:5000/api/client_parkings \
  -H "Content-Type: application/json" \
  -d '{"client_id":1,"parking_id":1}' \
  | python -m json.tool

# 4. Выехать с парковки
curl -X DELETE http://localhost:5000/api/client_parkings \
  -H "Content-Type: application/json" \
  -d '{"client_id":1,"parking_id":1}' \
  | python -m json.tool

# 5. Проверить историю клиента
curl http://localhost:5000/api/client_parkings/client/1 | python -m json.tool
```
