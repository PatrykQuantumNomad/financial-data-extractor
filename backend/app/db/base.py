"""
Database base configuration and session management.

This module provides SQLAlchemy setup for Alembic migrations and synchronous
database operations. The application primarily uses async connections via psycopg,
but SQLAlchemy models are needed for Alembic migrations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Settings

__all__ = ["Base", "engine", "SessionLocal"]

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

# Convert postgresql:// URL to postgresql+psycopg:// for psycopg3
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Create synchronous engine for migrations and synchronous operations
engine = create_engine(database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
