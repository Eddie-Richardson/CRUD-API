# CRUD-API/database.py

"""
Database setup for the Task API.

Owns everything about where task data lives: the SQLite engine, the
session factory, and the Task table definition. main.py never writes SQL
directly, it asks this module for a session and works with Task objects.
"""

from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# Engine + session setup
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def utcnow() -> datetime:
    """
    Returns the current UTC time.

    Returns:
        datetime: current time, timezone-aware, in UTC
    """
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Table definition
# ---------------------------------------------------------------------------


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------


def init_db():
    """
    Create the tasks table if it doesn't exist, and seed three example
    tasks the first time the app runs against an empty table.

    Returns:
        None
    """
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Task).count() == 0:
            db.add_all([
                Task(title="Buy groceries", done=False),
                Task(title="Finish project", done=True),
                Task(title="Call plumber", done=False),
            ])
            db.commit()
    finally:
        db.close()


def get_db():
    """
    FastAPI dependency that yields one database session per request.

    Returns:
        Session: a SQLAlchemy session, closed automatically after the
            request completes, even if the request raises.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
