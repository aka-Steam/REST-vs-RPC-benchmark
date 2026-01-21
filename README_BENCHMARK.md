# Руководство по проведению бенчмарков REST и gRPC сервисов

Это руководство описывает процесс проведения нагрузочного тестирования двух версий сервиса глоссария (REST на FastAPI и gRPC) с использованием Locust.

## Содержание

1. [Установка и настройка](#установка-и-настройка)
2. [Структура проекта](#структура-проекта)
3. [Подготовка тестовых данных](#подготовка-тестовых-данных)
4. [Запуск тестов](#запуск-тестов)
5. [Тестовые сценарии](#тестовые-сценарии)
6. [Интерпретация результатов](#интерпретация-результатов)
7. [Сравнение REST и gRPC](#сравнение-rest-и-grpc)

## Установка и настройка

### Требования

- Python 3.11+ (рекомендуется 3.12)
- Docker и Docker Compose (для запуска сервисов)
- Установленные зависимости из `requirements_benchmark.txt` (для запуска тестов)

### Установка зависимостей

**Важно:** Рекомендуется использовать виртуальное окружение для изоляции зависимостей.

```powershell
# Создать виртуальное окружение
python -m venv .venv

# Активировать виртуальное окружение (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Если возникает ошибка выполнения скриптов, выполните:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Установить зависимости
pip install -r requirements_benchmark.txt
```

**Примечание:** Виртуальное окружение должно быть активировано перед запуском всех команд Python.

### Настройка окружения

Скопируйте `env.example` в `.env` и настройте параметры при необходимости:

```powershell
copy env.example .env
```

Основные параметры:
- `REST_SERVICE_URL` - URL REST сервиса (по умолчанию `http://localhost:8000`)
- `GRPC_SERVICE_HOST` - Хост gRPC сервиса (по умолчанию `localhost`)
- `GRPC_SERVICE_PORT` - Порт gRPC сервиса (по умолчанию `50051`)

### Установка и настройка Docker

**Требования:**
- Docker Desktop (Windows/Mac) или Docker Engine (Linux)
- Docker Compose (обычно входит в состав Docker Desktop)

**Проверка установки:**
```powershell
# Проверить версию Docker
docker --version

# Проверить версию Docker Compose
docker compose version
```

**Первоначальная настройка:**
```powershell
# Собрать образы сервисов (при первом запуске)
docker compose build

# Или просто запустить (образы соберутся автоматически)
docker compose up -d
```

**Примечание:** При использовании Docker базы данных SQLite монтируются как volumes, поэтому данные сохраняются между перезапусками контейнеров. Файлы БД находятся в папках `glossary_RESTservice/` и `glossary_RPCservice/`.

## Структура проекта

```
benchmark/
├── locustfiles/              # Locust тестовые скрипты
│   ├── rest_user.py          # REST API тесты
│   ├── grpc_user.py          # gRPC тесты
│   └── common.py             # Общие утилиты
├── scripts/                   # Вспомогательные скрипты
│   ├── setup_test_data.py    # Подготовка тестовых данных
│   ├── cleanup_db.py         # Очистка БД
│   ├── run_benchmark.ps1     # Запуск одного теста
│   └── run_full_benchmark.ps1 # Запуск всех тестов
├── config/
│   └── test_scenarios.yaml    # Конфигурация сценариев
├── results/                   # Результаты тестов
│   ├── rest/                 # Результаты REST тестов
│   ├── grpc/                 # Результаты gRPC тестов
│   └── comparison/           # Сравнительные отчеты
└── requirements_benchmark.txt
```

## Подготовка тестовых данных

Перед запуском тестов рекомендуется подготовить тестовые данные в базах данных.

**Важно:** Убедитесь, что виртуальное окружение активировано и сервисы запущены (через Docker или вручную).

### Заполнение БД тестовыми данными

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# Заполнить обе БД 100 терминами
python scripts/setup_test_data.py --count 100

# Заполнить только REST БД
python scripts/setup_test_data.py --rest-only --count 50

# Заполнить только gRPC БД
python scripts/setup_test_data.py --grpc-only --count 50

# Очистить БД перед заполнением
python scripts/setup_test_data.py --count 100 --clear
```

**Примечание:** При использовании Docker базы данных монтируются как volumes, поэтому данные сохраняются между перезапусками контейнеров.

### Очистка БД

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# Очистить обе БД
python scripts/cleanup_db.py --yes

# Очистить только REST БД
python scripts/cleanup_db.py --rest-only --yes

# Очистить только gRPC БД
python scripts/cleanup_db.py --grpc-only --yes
```

## Запуск сервисов

Перед запуском тестов необходимо запустить оба сервиса. Рекомендуется использовать Docker для изоляции и удобства управления.

### Запуск через Docker (рекомендуется)

**Преимущества Docker:**
- Изоляция сервисов
- Единообразное окружение
- Простое управление (запуск/остановка)
- Автоматическая настройка сети

```powershell
# Запустить оба сервиса через Docker Compose
.\scripts\start_services_docker.ps1

# Или вручную:
docker compose up -d

# Проверить статус контейнеров
docker compose ps

# Просмотреть логи
docker compose logs -f

# Остановить сервисы
.\scripts\stop_services_docker.ps1
# Или: docker compose down
```

После запуска сервисы будут доступны на:
- REST сервис: `http://localhost:8000`
- gRPC сервис: `localhost:50051`

### Запуск без Docker (альтернативный способ)

Если Docker недоступен, можно запустить сервисы вручную:

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# Запустить оба сервиса в отдельных окнах
.\scripts\start_services.ps1
```

Или вручную:

**REST сервис:**
```powershell
# В отдельном окне PowerShell с активированным виртуальным окружением
.\scripts\start_rest_service.ps1

# Или вручную:
cd glossary_RESTservice
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**gRPC сервис:**
```powershell
# В отдельном окне PowerShell с активированным виртуальным окружением
.\scripts\start_grpc_service.ps1

# Или вручную:
cd glossary_RPCservice
python -m server.server
```

### Проверка доступности сервисов

**REST сервис:**
```powershell
# Проверить health endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Или открыть в браузере
# http://localhost:8000/docs (Swagger UI)
```

**gRPC сервис:**
```powershell
# Проверить через клиент (если запущен без Docker)
cd glossary_RPCservice
python -m client.cli list
```

**Проверка через Docker:**
```powershell
# Проверить статус контейнеров
docker compose ps

# Должны быть видны два контейнера в статусе "Up" и "healthy"
```

## Запуск тестов

### Запуск одного теста

**Важно:** Убедитесь, что виртуальное окружение активировано и сервисы запущены (через Docker или вручную).

#### Использование скрипта (рекомендуется)

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# REST тест с веб-интерфейсом
.\scripts\run_benchmark.ps1 -Service rest -Scenario sanity

# gRPC тест в headless режиме
.\scripts\run_benchmark.ps1 -Service grpc -Scenario stress -Headless
```

#### Прямой запуск Locust

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# REST тест с веб-интерфейсом
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000

# REST тест в headless режиме
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 1m

# gRPC тест в headless режиме
python -m locust -f locustfiles/grpc_user.py --headless -u 10 -r 2 -t 1m
```

### Запуск всех тестов автоматически

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# Запустить все сценарии для всех сервисов
.\scripts\run_full_benchmark.ps1

# Запустить только определенные сценарии
.\scripts\run_full_benchmark.ps1 -Scenarios sanity,normal

# Запустить только для REST сервиса
.\scripts\run_full_benchmark.ps1 -Services rest

# С автоматической очисткой и подготовкой данных
.\scripts\run_full_benchmark.ps1 -CleanupDB -SetupData -TestDataCount 100
```

## Тестовые сценарии

Все сценарии определены в `config/test_scenarios.yaml`:

### 1. Sanity Check (Легкая нагрузка)

**Цель:** Проверка работоспособности системы

- **Пользователи:** 10
- **Скорость создания:** 2 пользователя/сек
- **Длительность:** 1 минута
- **Ожидаемый RPS:** ~5
- **Ожидаемый p95:** < 200ms

### 2. Normal Load (Рабочая нагрузка)

**Цель:** Имитация нормального использования

- **Пользователи:** 50
- **Скорость создания:** 5 пользователей/сек
- **Длительность:** 5 минут
- **Ожидаемый RPS:** ~20
- **Ожидаемый p95:** < 500ms

### 3. Stress Test (Стресс-тест)

**Цель:** Выявление пределов производительности

- **Пользователи:** 200
- **Скорость создания:** 20 пользователей/сек
- **Длительность:** 3 минуты
- **Ожидаемый RPS:** ~80
- **Ожидаемый p95:** < 1000ms

### 4. Stability Test (Тест на стабильность)

**Цель:** Проверка деградации при длительной нагрузке

- **Пользователи:** 100
- **Скорость создания:** 10 пользователей/сек
- **Длительность:** 30 минут
- **Ожидаемый RPS:** ~40
- **Ожидаемый p95:** < 800ms

## Интерпретация результатов

### Метрики Locust

После завершения теста Locust предоставляет следующие метрики:

1. **RPS (Requests Per Second)** - Количество запросов в секунду
2. **Average Response Time** - Среднее время ответа
3. **Min/Max Response Time** - Минимальное/максимальное время ответа
4. **Median Response Time** - Медианное время ответа
5. **p95/p99** - 95-й и 99-й процентили времени ответа
6. **Failures** - Количество ошибок

### CSV файлы

Locust генерирует три CSV файла:

- `*_stats.csv` - Общая статистика по эндпоинтам
- `*_stats_history.csv` - История метрик во времени
- `*_failures.csv` - Детали ошибок

### HTML отчет

HTML отчет содержит:
- Графики RPS и времени ответа
- Таблицы статистики
- Детали ошибок

## Сравнение REST и gRPC

### Ключевые различия для анализа

1. **Пропускная способность (RPS)**
   - Сравните максимальный RPS для каждого сценария
   - Оцените влияние нагрузки на RPS

2. **Латентность**
   - Сравните среднее время ответа
   - Проанализируйте p95 и p99 процентили
   - Оцените влияние нагрузки на латентность

3. **Overhead**
   - Размер сообщений (REST JSON vs gRPC protobuf)
   - Network overhead
   - Сериализация/десериализация

4. **Деградация**
   - При каком количестве пользователей начинается деградация
   - Как изменяется производительность при росте нагрузки

### Рекомендации по анализу

1. Запустите одинаковые сценарии для обоих сервисов
2. Используйте одинаковые условия (одна машина, одно время)
3. Убедитесь, что БД содержат одинаковое количество данных
4. Сравните результаты по каждому сценарию отдельно

## Устранение неполадок

### Сервис недоступен

**Если используется Docker:**

```powershell
# Проверить статус контейнеров
docker compose ps

# Просмотреть логи для диагностики
docker compose logs rest-service
docker compose logs grpc-service

# Перезапустить сервисы
docker compose restart

# Пересобрать и перезапустить
docker compose up -d --build
```

**Если сервисы запущены без Docker:**

1. **REST сервис:**
   ```powershell
   # Убедитесь, что виртуальное окружение активировано
   .\.venv\Scripts\Activate.ps1
   cd glossary_RESTservice
   uvicorn app.main:app --reload
   ```

2. **gRPC сервис:**
   ```powershell
   # Убедитесь, что виртуальное окружение активировано
   .\.venv\Scripts\Activate.ps1
   cd glossary_RPCservice
   python -m server.server
   ```

### Ошибки импорта

Если возникают ошибки импорта:

1. **Убедитесь, что виртуальное окружение активировано:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Проверьте, что все зависимости установлены:**
   ```powershell
   pip install -r requirements_benchmark.txt
   ```

3. **Для gRPC тестов убедитесь, что protobuf файлы сгенерированы** (обычно они уже включены в проект)

4. **Проверьте, что вы находитесь в корневой директории проекта** при запуске скриптов

### Проблемы с Docker

**Контейнеры не запускаются:**
```powershell
# Проверить логи
docker compose logs

# Очистить и пересобрать
docker compose down
docker compose up -d --build
```

**Контейнеры в статусе "unhealthy":**
```powershell
# Просмотреть детальные логи
docker compose logs rest-service --tail 100
docker compose logs grpc-service --tail 100

# Проверить health checks
docker compose ps
```

**Проблемы с портами:**
- Убедитесь, что порты 8000 и 50051 свободны
- Проверьте, не запущены ли сервисы вручную на этих портах

### Низкая производительность

Если результаты показывают низкую производительность:

1. **Проверьте ресурсы системы** (CPU, RAM) - особенно важно при использовании Docker
2. **Убедитесь, что нет других процессов**, нагружающих систему
3. **Проверьте настройки БД** (SQLite может быть узким местом при высокой нагрузке)
4. **Рассмотрите использование более мощной машины** для тестов
5. **При использовании Docker** убедитесь, что контейнерам выделено достаточно ресурсов

## Дополнительные ресурсы

- [Документация Locust](https://docs.locust.io/)
- [gRPC документация](https://grpc.io/docs/)
- [FastAPI документация](https://fastapi.tiangolo.com/)

## Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Изучите файлы ошибок в `results/*/failures.csv`
3. Убедитесь, что все сервисы запущены и доступны

