# ToDo API

Учебное приложение для управления задачами по матрице Эйзенхауэра.

Можно создавать, изменять, завершать и удалять задачи, искать их, фильтровать по статусу и квадранту, получать статистику.

Используются FastAPI, Pydantic, SQLAlchemy и PostgreSQL (Supabase). Версия API — 2.0.0.

## Запуск

В терминале Git Bash:

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
pip install "sqlalchemy[asyncio]" asyncpg python-dotenv
```

Создайте в корне проекта файл `.env` и добавьте строку подключения из Supabase с префиксом `postgresql+asyncpg://`:

```dotenv
DATABASE_URL="СТРОКА_ПОДКЛЮЧЕНИЯ"
```

Файл `.env` содержит пароль и исключён из Git.

Проверьте подключение и запустите сервер:

```bash
python test_connection.py
uvicorn main:app --reload
```

При запуске приложения отсутствующие таблицы создаются автоматически.

## Проверка API

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Подключение к БД: http://127.0.0.1:8000/health

Маршруты задач начинаются с `/api/v2/tasks`, статистика доступна по `/api/v2/stats/`.

В Swagger выберите запрос, нажмите **Try it out**, заполните данные и нажмите **Execute**.

## Файлы проекта

- `main.py` — запуск приложения и подключение роутеров.
- `database.py` — подключение к БД и создание сессий.
- `models/task.py` — модель таблицы задач.
- `schemas.py` — проверка входных и выходных данных.
- `routers/tasks.py` — операции с задачами.
- `routers/stats.py` — статистика.
- `test_connection.py` — проверка подключения к БД.

Автор: Иван Ефремов.
