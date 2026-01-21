# Быстрый старт для запуска бенчмарков

Это краткое руководство поможет быстро начать работу с бенчмарками.

## Предварительные требования

- Python 3.11+ (рекомендуется 3.12)
- Docker и Docker Compose (для запуска сервисов)

## Установка зависимостей

**Важно:** Используйте виртуальное окружение для изоляции зависимостей.

```powershell
# Создать виртуальное окружение
python -m venv .venv

# Активировать виртуальное окружение (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Если возникает ошибка выполнения скриптов:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Установить зависимости
pip install -r requirements_benchmark.txt
```

## Запуск Locust тестов

### Важно для Windows
В Windows используйте `python -m locust` вместо просто `locust`, так как скрипты могут быть не в PATH.

**Важно:** Убедитесь, что виртуальное окружение активировано и сервисы запущены!

```powershell
# Активировать виртуальное окружение
.\.venv\Scripts\Activate.ps1
```

### REST API тесты

```powershell
# Запуск с веб-интерфейсом (по умолчанию http://localhost:8089)
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000

# Запуск в headless режиме (без веб-интерфейса)
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 1m

# Сохранение результатов в CSV
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 5m --csv results/rest/normal
```

### gRPC тесты

```powershell
# gRPC тест в headless режиме
python -m locust -f locustfiles/grpc_user.py --headless -u 10 -r 2 -t 1m
```

## Запуск сервисов

**Важно:** Перед запуском тестов необходимо запустить оба сервиса!

### Через Docker (рекомендуется)

```powershell
# Запустить оба сервиса через Docker Compose
.\scripts\start_services_docker.ps1

# Или вручную:
docker compose up -d

# Проверить статус
docker compose ps

# Остановить сервисы
.\scripts\stop_services_docker.ps1
# Или: docker compose down
```

### Без Docker (альтернативный способ)

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# Запустить оба сервиса автоматически (в отдельных окнах)
.\scripts\start_services.ps1

# Или запустить вручную в отдельных окнах:
.\scripts\start_rest_service.ps1
.\scripts\start_grpc_service.ps1
```

## Подготовка тестовых данных

```powershell
# Убедитесь, что виртуальное окружение активировано
.\.venv\Scripts\Activate.ps1

# Заполнить обе БД 100 терминами
python scripts/setup_test_data.py --count 100

# Очистить БД перед тестом
python scripts/cleanup_db.py --yes
```

## Параметры Locust

- `-f, --locustfile` - файл с тестами
- `-H, --host` - базовый URL сервиса (для REST)
- `-u, --users` - количество пользователей
- `-r, --spawn-rate` - скорость создания пользователей (в секунду)
- `-t, --run-time` - длительность теста (например: 1m, 5m, 30m)
- `--headless` - запуск без веб-интерфейса
- `--csv <prefix>` - сохранение результатов в CSV
- `--html <filename>` - сохранение HTML отчета

## Примеры сценариев

**Важно:** Убедитесь, что виртуальное окружение активировано перед запуском!

```powershell
.\.venv\Scripts\Activate.ps1
```

### Легкая нагрузка (sanity check)
```powershell
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 1m --csv results/rest/sanity
```

### Рабочая нагрузка
```powershell
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 5m --csv results/rest/normal
```

### Стресс-тест
```powershell
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000 --headless -u 200 -r 20 -t 3m --csv results/rest/stress
```

### Тест на стабильность
```powershell
python -m locust -f locustfiles/rest_user.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 30m --csv results/rest/stability
```

## Использование скриптов (рекомендуется)

Для более удобного запуска используйте готовые скрипты:

```powershell
# Запустить один тест
.\scripts\run_benchmark.ps1 -Service rest -Scenario sanity

# Запустить все тесты автоматически
.\scripts\run_full_benchmark.ps1
```

Подробнее см. [README_BENCHMARK.md](./README_BENCHMARK.md)

