from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


# Настройки для SQLite с поддержкой конкурентного доступа
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
        "timeout": 20.0,  # Таймаут ожидания блокировки БД (секунды)
    }
    
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    poolclass=StaticPool if settings.database_url.startswith("sqlite") else None,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    future=True,
)

# Включаем WAL режим для SQLite для лучшей конкурентности
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Баланс между производительностью и надежностью
        cursor.execute("PRAGMA busy_timeout=20000")  # Таймаут ожидания блокировки (мс)
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


