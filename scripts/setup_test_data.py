#!/usr/bin/env python3
"""
Script to populate databases with test data for benchmark testing.

Usage:
    python scripts/setup_test_data.py --rest-db glossary_RESTservice/glossary.db --grpc-db glossary_RPCservice/glossary.db --count 100
    python scripts/setup_test_data.py --rest-db glossary_RESTservice/glossary.db --count 50
    python scripts/setup_test_data.py --grpc-db glossary_RPCservice/glossary.db --count 50
"""

import argparse
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, func
from datetime import datetime
import random
import string


# Define Term model (same as in both services)
class Base(DeclarativeBase):
    pass


class Term(Base):
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    keyword: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


# Sample keywords and descriptions for realistic test data
SAMPLE_KEYWORDS = [
    "API", "REST", "gRPC", "HTTP", "HTTPS", "JSON", "XML", "SOAP",
    "GraphQL", "WebSocket", "TCP", "UDP", "DNS", "SSL", "TLS",
    "OAuth", "JWT", "Bearer", "CORS", "Cache", "CDN", "LoadBalancer",
    "Microservice", "Monolith", "Container", "Docker", "Kubernetes",
    "CI", "CD", "DevOps", "Agile", "Scrum", "Sprint", "Backlog",
    "Database", "SQL", "NoSQL", "MongoDB", "PostgreSQL", "Redis",
    "Elasticsearch", "Kafka", "RabbitMQ", "MessageQueue", "EventBus",
    "Async", "Sync", "Thread", "Process", "Coroutine", "Promise",
    "Observable", "Stream", "Buffer", "Queue", "Stack", "Heap",
    "Algorithm", "DataStructure", "BigO", "Complexity", "Optimization"
]

SAMPLE_DESCRIPTIONS = [
    "Application Programming Interface - набор протоколов и инструментов для создания программного обеспечения",
    "Representational State Transfer - архитектурный стиль для веб-сервисов",
    "gRPC Remote Procedure Calls - фреймворк для удаленного вызова процедур",
    "HyperText Transfer Protocol - протокол передачи данных в сети",
    "Secure HTTP - защищенная версия протокола HTTP",
    "JavaScript Object Notation - формат обмена данными",
    "eXtensible Markup Language - язык разметки",
    "Simple Object Access Protocol - протокол обмена сообщениями",
    "Graph Query Language - язык запросов для API",
    "Протокол для двусторонней связи через TCP",
    "Transmission Control Protocol - протокол управления передачей",
    "User Datagram Protocol - протокол пользовательских дейтаграмм",
    "Domain Name System - система доменных имен",
    "Secure Sockets Layer - уровень защищенных сокетов",
    "Transport Layer Security - протокол защиты транспортного уровня",
    "Open Authorization - открытый стандарт авторизации",
    "JSON Web Token - стандарт для безопасной передачи информации",
    "Токен доступа в формате Bearer",
    "Cross-Origin Resource Sharing - механизм безопасности браузера",
    "Кэш - временное хранилище данных для быстрого доступа",
    "Content Delivery Network - сеть доставки контента",
    "Балансировщик нагрузки - распределение запросов между серверами",
    "Микросервис - архитектурный подход с независимыми сервисами",
    "Монолит - единое приложение со всеми компонентами",
    "Контейнер - изолированная среда выполнения приложения",
    "Платформа для контейнеризации приложений",
    "Система оркестрации контейнеров",
    "Continuous Integration - непрерывная интеграция",
    "Continuous Deployment - непрерывное развертывание",
    "Разработка и эксплуатация - практика объединения процессов",
    "Гибкая методология разработки",
    "Фреймворк для управления проектами",
    "Короткий период разработки в Agile",
    "Список задач для выполнения",
    "База данных - организованное хранилище данных",
    "Structured Query Language - язык структурированных запросов",
    "Not Only SQL - нереляционные базы данных",
    "Документо-ориентированная NoSQL база данных",
    "Реляционная система управления базами данных",
    "In-memory хранилище данных типа ключ-значение",
    "Поисковая система на основе Apache Lucene",
    "Распределенная платформа потоковой обработки данных",
    "Система обмена сообщениями с очередями",
    "Очередь сообщений - механизм асинхронной коммуникации",
    "Шина событий - паттерн для обработки событий",
    "Асинхронный - выполнение без блокировки",
    "Синхронный - последовательное выполнение",
    "Поток выполнения программы",
    "Процесс - изолированная единица выполнения",
    "Сопрограмма - функция, которая может приостанавливать выполнение",
    "Обещание - объект, представляющий будущий результат",
    "Наблюдаемый - паттерн для работы с потоками данных",
    "Поток данных - последовательность элементов",
    "Буфер - временное хранилище данных",
    "Очередь - структура данных FIFO",
    "Стек - структура данных LIFO",
    "Куча - структура данных для приоритетной очереди",
    "Алгоритм - последовательность шагов для решения задачи",
    "Структура данных - способ организации данных",
    "Big O notation - обозначение сложности алгоритма",
    "Сложность - оценка ресурсов, необходимых алгоритму",
    "Оптимизация - улучшение производительности системы"
]


def generate_keyword(index: int = None) -> str:
    """Generate a unique keyword for testing."""
    if index is not None and index < len(SAMPLE_KEYWORDS):
        base = SAMPLE_KEYWORDS[index]
    else:
        base = random.choice(SAMPLE_KEYWORDS)
    
    # Add random suffix to ensure uniqueness
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{base}_{suffix}"


def generate_description(keyword: str = None) -> str:
    """Generate a test description."""
    if keyword and any(kw in keyword.upper() for kw in [k.upper() for k in SAMPLE_KEYWORDS]):
        # Try to match description to keyword
        for i, kw in enumerate(SAMPLE_KEYWORDS):
            if kw.upper() in keyword.upper():
                return SAMPLE_DESCRIPTIONS[i] if i < len(SAMPLE_DESCRIPTIONS) else f"Описание для {keyword}"
    
    # Fallback to random description
    desc = random.choice(SAMPLE_DESCRIPTIONS)
    # Add some variation
    variations = [" (тестовый термин)", " - тестовая запись", " [benchmark]"]
    return desc + random.choice(variations)


def setup_database(db_path: str, count: int, clear: bool = False):
    """
    Populate database with test data.
    
    Args:
        db_path: Path to SQLite database file
        count: Number of terms to create
        clear: Whether to clear existing data first
    """
    db_path = Path(db_path).resolve()
    
    if not db_path.parent.exists():
        print(f"Error: Directory {db_path.parent} does not exist")
        return False
    
    # Create database URL
    db_url = f"sqlite:///{db_path}"
    
    # Create engine and session
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        future=True
    )
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    
    try:
        if clear:
            # Clear existing data
            deleted = session.query(Term).delete()
            session.commit()
            print(f"  Cleared {deleted} existing terms from {db_path.name}")
        
        # Check current count
        current_count = session.query(Term).count()
        needed = count - current_count
        
        if needed <= 0:
            print(f"  Database {db_path.name} already has {current_count} terms (need {count})")
            return True
        
        print(f"  Adding {needed} terms to {db_path.name}...")
        
        # Generate and insert terms
        existing_keywords = {term.keyword for term in session.query(Term.keyword).all()}
        new_terms = []
        
        for i in range(needed):
            # Generate unique keyword
            attempts = 0
            while True:
                keyword = generate_keyword(i if i < len(SAMPLE_KEYWORDS) else None)
                if keyword not in existing_keywords:
                    existing_keywords.add(keyword)
                    break
                attempts += 1
                if attempts > 100:
                    # Fallback to timestamp-based keyword
                    keyword = f"TERM_{i}_{random.randint(100000, 999999)}"
                    break
            
            description = generate_description(keyword)
            term = Term(keyword=keyword, description=description)
            new_terms.append(term)
        
        session.add_all(new_terms)
        session.commit()
        
        final_count = session.query(Term).count()
        print(f"  ✓ Successfully populated {db_path.name} with {final_count} terms")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"  ✗ Error populating {db_path.name}: {e}")
        return False
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Populate databases with test data for benchmark testing"
    )
    parser.add_argument(
        "--rest-db",
        type=str,
        help="Path to REST service database file",
        default="glossary_RESTservice/glossary.db"
    )
    parser.add_argument(
        "--grpc-db",
        type=str,
        help="Path to gRPC service database file",
        default="glossary_RPCservice/glossary.db"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of test terms to create in each database (default: 100)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before populating"
    )
    parser.add_argument(
        "--rest-only",
        action="store_true",
        help="Only populate REST database"
    )
    parser.add_argument(
        "--grpc-only",
        action="store_true",
        help="Only populate gRPC database"
    )
    
    args = parser.parse_args()
    
    print(f"Setting up test data (count: {args.count}, clear: {args.clear})...")
    print()
    
    success = True
    
    if not args.grpc_only:
        print(f"REST Database: {args.rest_db}")
        if not setup_database(args.rest_db, args.count, args.clear):
            success = False
        print()
    
    if not args.rest_only:
        print(f"gRPC Database: {args.grpc_db}")
        if not setup_database(args.grpc_db, args.count, args.clear):
            success = False
        print()
    
    if success:
        print("✓ Test data setup completed successfully")
        sys.exit(0)
    else:
        print("✗ Test data setup completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()

