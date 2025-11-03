"""
Database fixtures for app and worker integration tests.

Provides testcontainer setup, database migrations, and test database sessions.

This file: Database fixtures (testcontainers, migrations, sessions)

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from testcontainers.postgres import PostgresContainer

from alembic import command
from app import create_app
from app.db.base import get_session_maker
from config import Settings
from tests.integration.conftest import _restore_env_vars, _setup_test_env


def _parse_db_url(db_url: str) -> dict[str, str]:
    """Parse database URL into components.

    Args:
        db_url: Database connection URL.

    Returns:
        Dictionary with host, port, db_name, username, password.
    """
    clean_url = db_url.replace("postgresql+psycopg://", "postgresql://").replace(
        "postgresql+psycopg3://", "postgresql://"
    )
    parsed = urlparse(clean_url)

    return {
        "host": parsed.hostname or "localhost",
        "port": str(parsed.port or 5432),
        "db_name": parsed.path.lstrip("/"),
        "username": unquote(parsed.username or "test"),
        "password": unquote(parsed.password or "test"),
    }


@pytest.fixture(scope="session")
def postgres_container():
    """Create a PostgreSQL testcontainer for integration tests."""
    with PostgresContainer("postgres:16", driver="psycopg3") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_url(postgres_container):
    """Get database connection URL from testcontainer."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def alembic_cfg(db_url):
    """Create Alembic config with testcontainer database URL."""
    backend_path = Path(__file__).resolve().parent.parent.parent.parent
    alembic_ini = backend_path / "alembic.ini"
    alembic_db_url = db_url.replace("postgresql+psycopg3://", "postgresql://")

    original_database_url = os.environ.get("DATABASE_URL")

    try:
        os.environ["DATABASE_URL"] = alembic_db_url
        cfg = Config(str(alembic_ini))
        cfg.set_main_option("script_location", str(backend_path / "alembic"))
        yield cfg
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url


@pytest.fixture(scope="session", autouse=True)
def database_initialized(db_url, alembic_cfg):
    """Run database migrations to initialize schema."""
    command.upgrade(alembic_cfg, "head")


@pytest.fixture
def db_pool(db_url):
    """Create database connection pool for testing."""
    pool = AsyncConnectionPool(
        conninfo=db_url, max_size=10, kwargs={"autocommit": True, "row_factory": dict_row}
    )
    yield pool
    pool.close()


@pytest.fixture
def test_settings(db_url):
    """Create test settings with database URL from testcontainer."""
    db_params = _parse_db_url(db_url)
    env_overrides = {
        "db_host": db_params["host"],
        "db_port": db_params["port"],
        "db_name": db_params["db_name"],
        "db_username": db_params["username"],
        "db_password": db_params["password"],
    }

    original_env = _setup_test_env(env_overrides)

    try:
        yield Settings()
    finally:
        _restore_env_vars(original_env)


@pytest.fixture
def test_app(database_initialized, db_url):
    """Create FastAPI test application with testcontainer database."""
    db_params = _parse_db_url(db_url)

    # Only override DB-related env vars for app creation
    db_env_overrides = {
        "db_host": db_params["host"],
        "db_port": db_params["port"],
        "db_name": db_params["db_name"],
        "db_username": db_params["username"],
        "db_password": db_params["password"],
    }

    # Store minimal set of env vars that app needs
    original_env = {}
    app_env_keys = ["db_host", "db_port", "db_name", "db_username", "db_password"]
    for key in app_env_keys:
        original_env[key] = os.environ.get(key)

    try:
        _setup_test_env(db_env_overrides)
        app = create_app()
        yield app
    finally:
        _restore_env_vars(original_env)


@pytest.fixture
def test_client(test_app):
    """Create test client for FastAPI app with proper lifespan handling."""
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
async def test_db_session(db_url):
    """Create async database session for worker tests.

    This fixture creates a SQLAlchemy async session using the testcontainer database.
    The session is automatically closed after the test.
    """
    session_maker = get_session_maker(db_url)

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
