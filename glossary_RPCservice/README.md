## Интерактивный глоссарий терминов для ВКР. RPC версия

Сервис глоссария  на Python с использованием gRPC, protobuf и SQLAlchemy/Alembic.

### Операции
- Получение списка терминов
- Получение термина по ключевому слову
- Создание термина
- Обновление термина
- Удаление термина

Основано на идеях примера gRPC-сервиса и учебной тетради (ссылки в конце).

### Требования
- Python 3.12+
- Windows PowerShell (команды ниже под PowerShell)

### Структура проекта
```
app/                 # конфиг, БД, модели
client/              # простой gRPC-клиент (CLI)
proto/               # protobuf-схемы (glossary.proto)
server/              # gRPC-сервер
alembic/             # миграции БД
alembic.ini
requirements.txt
README.md
```

### Установка и запуск
1) Создать и активировать окружение, установить зависимости
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

2) Сгенерировать Python-стабы из protobuf-схемы
```powershell
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto\glossary.proto
```
Должны появиться файлы `glossary_pb2.py` и `glossary_pb2_grpc.py` в корне проекта.

3) (Опционально) настроить БД через переменные окружения
- По умолчанию используется SQLite: `sqlite:///./glossary.db`
- Переопределить можно так:
```powershell
$env:APP_DATABASE_URL = "sqlite:///./glossary.db"
```

4) Запустить gRPC-сервер
```powershell
python -m server.server
```
При старте запускаются миграции Alembic (`alembic upgrade head`). Если Alembic недоступен, будет выполнено создание таблиц через SQLAlchemy. По умолчанию сервер слушает порт `50051`.

### Ручная проверка (CLI-клиент)
В новом окне PowerShell:
```powershell
# список терминов
python -m client.cli list

# создать термин
python -m client.cli create HTTP "Протокол передачи гипертекста"

# получить термин
python -m client.cli get HTTP

# обновить термин
python -m client.cli update HTTP "Обновленное описание протокола HTTP"

# удалить термин
python -m client.cli delete HTTP

# снова список
python -m client.cli list
```
Ожидаемое:
- `get` несуществующего ключа → NOT_FOUND
- повторный `create` того же ключа → ALREADY_EXISTS

### Тестирование через grpcurl (опционально)
```powershell
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext -d "{}" localhost:50051 glossary.GlossaryService.ListTerms
grpcurl -plaintext -d "{\"item\":{\"keyword\":\"HTTP\",\"description\":\"...\"}}" localhost:50051 glossary.GlossaryService.CreateTerm
```

### Примечания по миграциям
- Миграции Alembic в `alembic/versions/`
- Ручной запуск:
```powershell
alembic upgrade head
```
- Сервер при запуске пытается автоматически применить миграции, иначе вызывает `create_all`.