# Интерактивный глоссарий терминов для ВКР

Cервис глоссария на FastAPI с хранением в SQLite и миграциями через Alembic.

## Структура проекта (основное)

```
app/
  main.py            # Точка входа FastAPI, /health, подключение роутеров
  config.py          # Настройки (DATABASE_URL)
  db.py              # Движок и сессии SQLAlchemy, зависимость get_db
  models.py          # ORM-модель Term
  schemas.py         # Pydantic-схемы TermCreate/Update/Out
  routers/
    terms.py         # CRUD-эндпоинты для терминов
alembic/
  env.py             # Конфиг Alembic, target_metadata
  versions/
    0001_init_terms.py
alembic.ini
requirements.txt
```

## Быстрый старт

Требования: Python 3.11+ (рекомендуется 3.12)

```powershell
# 1) Создать и активировать виртуальное окружение (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt

# 3) Применить миграции (создаст файл базы данных glossary.db)
alembic upgrade head

# 4) Запустить приложение
uvicorn app.main:app --reload
```

Откройте документацию:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Проверка здоровья:

```
GET http://127.0.0.1:8000/health
```

## Конфигурация

- По умолчанию: `DATABASE_URL = sqlite:///./glossary.db`

- Можно переопределить через переменную окружения `APP_DATABASE_URL` или файл `.env`:
  
  ```
  APP_DATABASE_URL=sqlite:///./glossary.db
  ```
  
  ## Эндпоинты глоссария
  
  Базовый префикс: `/terms`

- GET `/terms` — список всех терминов

- GET `/terms/{keyword}` — получить термин по ключевому слову

- POST `/terms` — добавить термин

- PUT `/terms/{keyword}` — обновить термин

- DELETE `/terms/{keyword}` — удалить термин

## Текущее состояние

- [x] Базовый каркас FastAPI (`/health`, подключение роутера `terms`)
- [x] Модель `Term` и схемы Pydantic (`TermCreate`, `TermUpdate`, `TermOut`)
- [x] Инициализация Alembic и первая миграция (создание таблицы `terms`)
- [x] CRUD-эндпоинты для терминов
- [ ] Контейнеризация (Docker/Docker Compose)
- [ ] CI/CD, тесты


