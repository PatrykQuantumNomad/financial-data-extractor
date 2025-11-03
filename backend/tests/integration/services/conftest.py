"""
Service-specific test fixtures that don't require database.

This conftest provides minimal fixtures for service component tests without
starting testcontainers or running Alembic migrations.

Service tests (scraping, PDF extraction, normalization, compilation) typically
don't need a database - they test pure business logic.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest

from config import Settings
from tests.integration.conftest import _restore_env_vars, _setup_test_env


@pytest.fixture
def test_settings_services():
    """Create test settings for service tests.

    This fixture only loads Settings with values from .env files.
    No database connection or testcontainers needed.
    """
    original_env = _setup_test_env()

    try:
        yield Settings()
    finally:
        _restore_env_vars(original_env)
