"""
Database base configuration and session management.

This module provides SQLAlchemy setup for both Alembic migrations (synchronous)
and runtime operations (async). The sync engine is used for migrations,
while the async engine is used for application runtime operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Settings

__all__ = ["Base", "engine", "SessionLocal", "async_engine", "AsyncSessionLocal"]

# Create declarative base for models
# Models will import this Base and register themselves with Base.metadata
Base = declarative_base()


# Import all models after Base is created to register them with Base.metadata
# This import happens at the module level to ensure models are loaded
def _import_models() -> None:
    """Import all models to register them with Base.metadata."""
    from app.db.models.company import Company  # noqa: F401
    from app.db.models.document import Document  # noqa: F401
    from app.db.models.extraction import CompiledStatement, Extraction  # noqa: F401


# Call the function to trigger imports
_import_models()

# Get database URL from settings or environment variable
# Priority: DATABASE_URL env var > Settings object
database_url = os.getenv("DATABASE_URL")
if not database_url:
    try:
        settings = Settings()
        database_url = settings.database_url
    except Exception:
        # Fallback to alembic.ini default
        database_url = "postgresql://postgres:postgres@localhost:5432/financial_data_extractor"

# Convert postgresql:// URL to postgresql+psycopg:// for psycopg3 (sync)
if database_url.startswith("postgresql://"):
    database_url_sync = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    database_url_sync = database_url

# Convert to async URL format (postgresql+psycopg for async)
if database_url.startswith("postgresql://"):
    database_url_async = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    database_url_async = database_url

# Create synchronous engine for migrations and synchronous operations
engine = create_engine(database_url_sync, pool_pre_ping=True, pool_size=10, max_overflow=20)

# Create session factory for synchronous operations (migrations)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create async engine for runtime operations
async_engine = create_async_engine(
    database_url_async,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    echo=False,
)

# Create async session factory for runtime operations
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
