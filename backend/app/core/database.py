"""
Database connection and session management.
Provides SQLAlchemy engine, session maker, and dependency injection for FastAPI.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from loguru import logger

from .config import settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)


# Event listener to set MySQL session variables
@event.listens_for(engine, "connect")
def set_mysql_pragma(dbapi_conn, connection_record):
    """Set MySQL session variables on connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'")
    cursor.execute("SET SESSION time_zone='+00:00'")  # Use UTC
    cursor.close()


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.
    
    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in models.
    
    Note: In production, use Alembic migrations instead.
    """
    logger.info("Initializing database tables...")
    try:
        # Import all models here to ensure they're registered
        from app.models import user, book, club, club_member, reading_progress, discussion
        
        Base.metadata.create_all(bind=engine)
        logger.success("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def close_db() -> None:
    """Close database connections and dispose engine."""
    logger.info("Closing database connections...")
    engine.dispose()
    logger.success("Database connections closed")

