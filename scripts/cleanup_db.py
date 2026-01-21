#!/usr/bin/env python3
"""
Script to clean up test data from databases.

Usage:
    python scripts/cleanup_db.py --rest-db glossary_RESTservice/glossary.db --grpc-db glossary_RPCservice/glossary.db
    python scripts/cleanup_db.py --rest-db glossary_RESTservice/glossary.db
    python scripts/cleanup_db.py --grpc-db glossary_RPCservice/glossary.db
"""

import argparse
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, func
from datetime import datetime


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


def cleanup_database(db_path: str, confirm: bool = False):
    """
    Remove all terms from database.
    
    Args:
        db_path: Path to SQLite database file
        confirm: Whether to skip confirmation prompt
    """
    db_path = Path(db_path).resolve()
    
    if not db_path.exists():
        print(f"  Warning: Database {db_path.name} does not exist")
        return False
    
    if not confirm:
        response = input(f"  Are you sure you want to delete all terms from {db_path.name}? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print(f"  Skipped {db_path.name}")
            return False
    
    # Create database URL
    db_url = f"sqlite:///{db_path}"
    
    # Create engine and session
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        future=True
    )
    
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    
    try:
        # Count existing terms
        count_before = session.query(Term).count()
        
        if count_before == 0:
            print(f"  Database {db_path.name} is already empty")
            return True
        
        # Delete all terms
        deleted = session.query(Term).delete()
        session.commit()
        
        print(f"  ✓ Deleted {deleted} terms from {db_path.name}")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"  ✗ Error cleaning {db_path.name}: {e}")
        return False
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Clean up test data from databases"
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
        "--rest-only",
        action="store_true",
        help="Only clean REST database"
    )
    parser.add_argument(
        "--grpc-only",
        action="store_true",
        help="Only clean gRPC database"
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    args = parser.parse_args()
    
    print("Cleaning up test data from databases...")
    print()
    
    success = True
    
    if not args.grpc_only:
        print(f"REST Database: {args.rest_db}")
        if not cleanup_database(args.rest_db, confirm=args.yes):
            success = False
        print()
    
    if not args.rest_only:
        print(f"gRPC Database: {args.grpc_db}")
        if not cleanup_database(args.grpc_db, confirm=args.yes):
            success = False
        print()
    
    if success:
        print("✓ Database cleanup completed successfully")
        sys.exit(0)
    else:
        print("✗ Database cleanup completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()

