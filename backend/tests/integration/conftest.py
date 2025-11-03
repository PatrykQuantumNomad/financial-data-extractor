"""
Common fixtures and documentation for integration tests.

This is the parent conftest.py for all integration tests.
It provides common fixtures used across all integration test directories.

Integration tests are organized by component type:
- app/: FastAPI application integration tests (require database)
- services/: Service component tests (pure business logic, no database)
- workers/: Worker integration tests (require database)

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Common environment variable keys used across test fixtures
ENV_KEYS = [
    "db_host",
    "db_port",
    "db_name",
    "db_username",
    "db_password",
    "redis_host",
    "redis_port",
    "redis_db",
    "redis_password",
    "open_router_api_key",
    "minio_endpoint",
    "minio_access_key",
    "minio_secret_key",
]

# Environment variable compatibility mapping (lowercase -> UPPERCASE)
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
    ("open_router_api_key", "OPEN_ROUTER_API_KEY"),
    ("minio_endpoint", "MINIO_ENDPOINT"),
    ("minio_access_key", "MINIO_ACCESS_KEY"),
    ("minio_secret_key", "MINIO_SECRET_KEY"),
]

# Test environment defaults
TEST_ENV_DEFAULTS = {
    "db_host": "localhost",
    "db_port": "5432",
    "db_name": "test_db",
    "db_username": "test_user",
    "db_password": "test_password",
    "redis_host": "localhost",
    "redis_port": "6379",
    "redis_db": "0",
    "redis_password": "test_password",
    "open_router_api_key": "test_key",
    "minio_endpoint": "localhost:9000",
    "minio_access_key": "minioadmin",
    "minio_secret_key": "minioadmin",
}


@pytest.fixture(scope="session", autouse=True)
def load_env_files():
    """Load .env files early so they're available at test collection time.

    This fixture checks for .env files in the integration test folder (and subfolders) first,
    then falls back to the backend .env for dev/app-wide defaults.

    Loads .env files in order of precedence:
    1. Closest .env in the integration test file's directory (or subdir)
    2. Backend .env (used in dev/app) as fallback base values
    """
    from dotenv import find_dotenv

    test_dir = Path(__file__).resolve().parent  # backend/tests/integration
    backend_dir = test_dir.parent.parent  # backend/
    integration_env_file = find_dotenv(
        str(test_dir / ".env"), raise_error_if_not_found=False, usecwd=True
    )
    backend_env_file = backend_dir / ".env"

    # 1. Load integration test .env (if exists, search upwards from integration test dir)
    if integration_env_file:
        load_dotenv(integration_env_file, override=False)
    else:
        # Also search for .env in any subfolder (per-test .env setup)
        for env_path in test_dir.rglob(".env"):
            load_dotenv(env_path, override=False)

    # 2. Backend-level fallback .env (development)
    if backend_env_file.exists():
        load_dotenv(backend_env_file, override=False)

    yield


def _restore_env_vars(original_env: dict[str, str | None]) -> None:
    """Restore original environment variables."""
    for key in ENV_KEYS:
        if original_env.get(key) is not None:
            os.environ[key] = original_env[key]
        else:
            os.environ.pop(key, None)


def _setup_test_env(env_overrides: dict[str, str] | None = None) -> dict[str, str | None]:
    """Set up test environment variables.

    Args:
        env_overrides: Optional dictionary of environment variable overrides.

    Returns:
        Dictionary of original environment variable values for restoration.
    """
    original_env = {key: os.environ.get(key) for key in ENV_KEYS}

    # Apply overrides first
    if env_overrides:
        for key, value in env_overrides.items():
            os.environ[key] = value

    # Set defaults for missing values
    for key, value in TEST_ENV_DEFAULTS.items():
        os.environ.setdefault(key, value)

    # Apply compatibility mapping (UPPERCASE > lowercase)
    for lower, upper in ENV_COMPAT_KEYS:
        if upper in os.environ:
            os.environ[lower] = os.environ[upper]

    return original_env
