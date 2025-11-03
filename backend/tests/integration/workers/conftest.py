"""
Scraping-specific test fixtures that don't require database.

This conftest provides minimal fixtures for scraping tests without
starting testcontainers or running Alembic migrations.

It overrides the database_initialized fixture to do nothing,
preventing testcontainer and Alembic from running.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Import Settings from config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import Settings


# Override database-related fixtures to prevent testcontainer and Alembic from running
@pytest.fixture(scope="session")
def postgres_container():
    """Override: Skip postgres container for scraping tests."""
    yield None  # Return None instead of starting container


@pytest.fixture(scope="session")
def db_url():
    """Override: Skip database URL setup for scraping tests."""
    yield ""  # Return empty string


@pytest.fixture(scope="session")
def alembic_cfg():
    """Override: Skip Alembic config for scraping tests."""
    yield None  # Return None


@pytest.fixture(scope="session", autouse=True)
def database_initialized():
    """Override: Skip database initialization for scraping tests."""
    yield  # Do nothing, just yield


@pytest.fixture(scope="session", autouse=True)
def load_env_files_scraping():
    """Load .env files early for scraping tests (no database needed).

    This fixture runs automatically before scraping tests are collected.
    """
    # Get project root directory
    backend_dir = Path(__file__).resolve().parent.parent.parent
    project_root = backend_dir.parent
    root_env_file = project_root / ".env"
    backend_env_file = backend_dir / ".env"

    # Load .env files in order of precedence:
    # 1. Backend .env (if exists) - loaded first as base values
    if backend_env_file.exists():
        load_dotenv(backend_env_file, override=False)

    # 2. Root .env (if exists) - takes precedence over backend .env
    if root_env_file.exists():
        load_dotenv(root_env_file, override=True)

    yield


@pytest.fixture
def test_settings_scraping():
    """Create test settings for scraping tests without database.

    This fixture only loads Settings with values from .env files.
    No database connection or testcontainers needed.
    """
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

        # Set required env vars with test defaults if not already set from .env
        # These are needed for Settings initialization but won't be used by scraping service
        os.environ.setdefault("db_host", "localhost")
        os.environ.setdefault("db_port", "5432")
        os.environ.setdefault("db_name", "test_db")
        os.environ.setdefault("db_username", "test_user")
        os.environ.setdefault("db_password", "test_password")
        os.environ.setdefault("redis_host", "localhost")
        os.environ.setdefault("redis_port", "6379")
        os.environ.setdefault("redis_db", "0")
        os.environ.setdefault("redis_password", "test_password")
        os.environ.setdefault("openai_api_key", "test_key")
        os.environ.setdefault("open_router_api_key", "test_key")
        os.environ.setdefault("minio_endpoint", "localhost:9000")
        os.environ.setdefault("minio_access_key", "minioadmin")
        os.environ.setdefault("minio_secret_key", "minioadmin")

        # Use upper-case environment variable values for Settings if present
        # Priority: UPPERCASE (real secrets from environment) over lowercase (test/dummy)
        env_compat_keys = [
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
        for lower, upper in env_compat_keys:
            if upper in os.environ:
                os.environ[lower] = os.environ[upper]

        # Create settings with env vars (Settings will read from os.environ)
        settings = Settings()

        yield settings

    finally:
        # Restore original env vars
        for key in env_keys:
            if original_env.get(key) is not None:
                os.environ[key] = original_env[key]
            else:
                os.environ.pop(key, None)
