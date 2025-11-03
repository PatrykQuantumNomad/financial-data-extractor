"""
Shared fixtures for integration tests.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import pytest
from alembic.config import Config
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from testcontainers.postgres import PostgresContainer

from alembic import command

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app import create_app
from config import Settings


@pytest.fixture(scope="session", autouse=True)
def load_env_files():
    """Load .env files early so they're available at test collection time.

    This fixture runs automatically before any tests are collected,
    making .env values available for @pytest.mark.skipif decorators.
    """
    # Get project root directory (parent of backend directory)
    backend_dir = Path(__file__).resolve().parent.parent.parent
    project_root = backend_dir.parent
    root_env_file = project_root / ".env"
    backend_env_file = backend_dir / ".env"

    # Load .env files in order of precedence:
    # 1. Backend .env (if exists) - loaded first as base values
    if backend_env_file.exists():
        load_dotenv(backend_env_file, override=False)

    # 2. Root .env (if exists) - takes precedence over backend .env
    # override=True allows root .env to override backend .env values
    if root_env_file.exists():
        load_dotenv(root_env_file, override=True)

    yield


@pytest.fixture(scope="session")
def postgres_container():
    """Create a PostgreSQL testcontainer for integration tests."""
    # Start PostgreSQL 16 container
    with PostgresContainer("postgres:16", driver="psycopg3") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_url(postgres_container):
    """Get database connection URL from testcontainer."""
    # Get connection URL from container (already in psycopg3 format)
    db_url = postgres_container.get_connection_url()
    return db_url


@pytest.fixture(scope="session")
def alembic_cfg(db_url):
    """Create Alembic config with testcontainer database URL."""
    # Get alembic.ini path
    backend_dir = Path(__file__).resolve().parent.parent.parent
    alembic_ini = backend_dir / "alembic.ini"

    # Convert postgresql+psycopg3:// to postgresql:// for Alembic
    # Alembic's env.py will handle the conversion back to psycopg
    alembic_db_url = db_url.replace("postgresql+psycopg3://", "postgresql://")

    # Store original DATABASE_URL if it exists
    original_database_url = os.environ.get("DATABASE_URL")

    try:
        # Set DATABASE_URL env var so Alembic's env.py picks it up
        os.environ["DATABASE_URL"] = alembic_db_url

        # Create config
        cfg = Config(str(alembic_ini))

        # Set script location
        cfg.set_main_option("script_location", str(backend_dir / "alembic"))

        yield cfg

    finally:
        # Restore original DATABASE_URL
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url


@pytest.fixture(scope="session", autouse=True)
def database_initialized(db_url, alembic_cfg):
    """Run database migrations to initialize schema."""
    # Run migrations
    command.upgrade(alembic_cfg, "head")


@pytest.fixture
def db_pool(db_url):
    """Create database connection pool for testing."""
    # Create pool
    pool = AsyncConnectionPool(
        conninfo=db_url, max_size=10, kwargs={"autocommit": True, "row_factory": dict_row}
    )
    yield pool
    pool.close()


@pytest.fixture
def test_settings(db_url):
    """Create test settings with database URL from testcontainer.

    Loads values from root .env file first, then applies test overrides.
    Test defaults are only used if values aren't in .env or environment.
    """
    # Get project root directory
    backend_dir = Path(__file__).resolve().parent.parent.parent

    # Parse URL using urlparse for proper handling of special characters
    clean_url = db_url.replace("postgresql+psycopg://", "postgresql://")

    parsed = urlparse(clean_url)
    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    db_name = parsed.path.lstrip("/")
    username = unquote(parsed.username or "test")
    password = unquote(parsed.password or "test")

    # Store original env vars
    original_env = {}
    env_keys = [
        "db_host",
        "db_port",
        "db_name",
        "db_username",
        "db_password",
        "redis_host",
        "redis_port",
        "redis_db",
        "redis_password",
        "openai_api_key",
        "open_router_api_key",
        "minio_endpoint",
        "minio_access_key",
        "minio_secret_key",
    ]

    try:
        # Store original values
        for key in env_keys:
            original_env[key] = os.environ.get(key)

        # Load .env files in order of precedence:
        # 1. Backend .env (if exists) - loaded first as base values
        backend_env_file = backend_dir / ".env"
        if backend_env_file.exists():
            load_dotenv(backend_env_file, override=False)

        # Override database settings with testcontainer values (always use test DB)
        os.environ["db_host"] = host
        os.environ["db_port"] = port
        os.environ["db_name"] = db_name
        os.environ["db_username"] = username
        os.environ["db_password"] = password

        # Set required env vars with test defaults ONLY if not already set from .env
        # This allows .env values to be used when available
        os.environ.setdefault("redis_host", "localhost")
        os.environ.setdefault("redis_port", "6379")
        os.environ.setdefault("redis_db", "0")
        os.environ.setdefault("redis_password", "test_password")
        os.environ.setdefault("openai_api_key", "test_key")
        os.environ.setdefault("open_router_api_key", "test_key")
        os.environ.setdefault("minio_endpoint", "localhost:9000")
        os.environ.setdefault("minio_access_key", "minioadmin")
        os.environ.setdefault("minio_secret_key", "minioadmin")

        # Use upper-case environment variable values for Settings if present (test runs may set both)
        # Priority: UPPERCASE (real secrets from environment) over lowercase (test/dummy)
        # This is a temporary patch until config is fully standardized

        # Patch: overwrite lower-case os.environ keys with UPPERCASE if set (avoids 'test_key' leakage)
        ENV_COMPAT_KEYS = [
            ("db_host", "DB_HOST"),
            ("db_port", "DB_PORT"),
            ("db_name", "DB_NAME"),
            ("db_username", "DB_USERNAME"),
            ("db_password", "DB_PASSWORD"),
            ("redis_host", "REDIS_HOST"),
            ("redis_port", "REDIS_PORT"),
            ("redis_db", "REDIS_DB"),
            ("redis_password", "REDIS_PASSWORD"),
            ("openai_api_key", "OPENAI_API_KEY"),
            ("open_router_api_key", "OPEN_ROUTER_API_KEY"),
            ("minio_endpoint", "MINIO_ENDPOINT"),
            ("minio_access_key", "MINIO_ACCESS_KEY"),
            ("minio_secret_key", "MINIO_SECRET_KEY"),
        ]
        for lower, upper in ENV_COMPAT_KEYS:
            if upper in os.environ:
                os.environ[lower] = os.environ[upper]

        # Create settings with corrected env vars (Settings will read from os.environ)
        settings = Settings()

        yield settings

    finally:
        # Restore original env vars
        for key in env_keys:
            if original_env.get(key) is not None:
                os.environ[key] = original_env[key]
            else:
                os.environ.pop(key, None)


@pytest.fixture
def test_app(database_initialized, db_url):
    """Create FastAPI test application with testcontainer database."""
    # Set up environment variables for testcontainer
    # Parse URL using urlparse for proper handling of special characters in password
    # testcontainers returns: postgresql+psycopg://test:test@localhost:5432/test
    # We need to normalize it first
    clean_url = db_url.replace("postgresql+psycopg://", "postgresql://")

    parsed = urlparse(clean_url)
    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    db_name = parsed.path.lstrip("/")
    username = unquote(parsed.username or "test")
    password = unquote(parsed.password or "test")

    # Store original
    original_env = {}
    env_keys = [
        "db_host",
        "db_port",
        "db_name",
        "db_username",
        "db_password",
        "redis_host",
        "redis_port",
        "redis_password",
        "openai_api_key",
    ]

    try:
        # Set test env vars
        os.environ["db_host"] = host
        os.environ["db_port"] = port
        os.environ["db_name"] = db_name
        os.environ["db_username"] = username
        os.environ["db_password"] = password
        os.environ["redis_host"] = "localhost"
        os.environ["redis_port"] = "6379"
        os.environ["redis_password"] = "test_password"
        os.environ["openai_api_key"] = "test_key"

        # Create app with test settings
        app = create_app()

        # Replace db_pool in app state with our test pool
        # We need to handle this in a lifecycle-aware way
        # For now, we'll let the app create its own pool via lifespan

        yield app

    finally:
        # Restore environment
        for key in env_keys:
            if key in original_env:
                os.environ[key] = original_env[key]
            else:
                os.environ.pop(key, None)


@pytest.fixture
def test_client(test_app):
    """Create test client for FastAPI app with proper lifespan handling."""
    with TestClient(test_app) as client:
        yield client
