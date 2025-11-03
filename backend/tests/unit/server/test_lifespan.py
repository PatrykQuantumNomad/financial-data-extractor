"""
Unit tests for the `lifespan.py` module of the `src.agent` package.

This module tests the `LifespanManager` class, ensuring that it correctly
manages the lifespan of the FastAPI application, including initializing and
cleaning up essential resources such as the database connection pool.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from app.lifespan import LifespanManager
from config import Settings


@pytest.fixture(name="mock_settings")
def fixture_mock_settings() -> Settings:
    """
    Fixture to create a mock Settings instance with necessary configuration.

    Returns:
        Settings: The mocked Settings instance.
    """
    return Settings(
        db_host="localhost",
        db_port=5432,
        db_name="test_db",
        db_username="test_user",
        db_password="test_password",
        redis_host="localhost",
        redis_port=6379,
        redis_db=0,
        redis_password="test_password",
        open_router_api_key="test_api_key",
        minio_endpoint="localhost:9000",
        minio_access_key="minioadmin",
        minio_secret_key="minioadmin",
        minio_bucket_name="financial-documents",
        minio_use_ssl=False,
        server_log_level="info",
        app_log_level="debug",
        logging_path="logging.json",
        app_name="financial-data-extractor-api",
        app_version="1.0.0",
        # Override any other settings if needed
    )


@pytest.fixture(name="mock_logger")
def fixture_mock_logger() -> MagicMock:
    """
    Fixture to create a mock logger instance.

    Returns:
        MagicMock: The mocked logger instance.
    """
    return MagicMock()


@pytest.fixture(name="lifespan_manager")
def fixture_lifespan_manager(mock_settings: Settings, mock_logger: MagicMock) -> LifespanManager:
    """
    Fixture to create an instance of LifespanManager.

    Args:
        mock_settings (Settings): The mocked Settings instance.
        mock_logger (MagicMock): The mocked logger instance.

    Returns:
        LifespanManager: The instance of LifespanManager.
    """
    return LifespanManager(settings=mock_settings, logger=mock_logger)


@pytest.mark.asyncio
async def test_lifespan_startup_initializes_resources(
    lifespan_manager: LifespanManager, mock_settings: Settings
):
    """
    Test that the lifespan startup initializes essential resources, such as the
    database connection pool.

    Args:
        lifespan_manager (LifespanManager): The instance of LifespanManager used for testing.
        mock_settings (Settings): The mocked Settings instance.
    """
    app = FastAPI()
    app.state.settings = mock_settings

    mock_engine = AsyncMock()
    # Mock the dispose method for cleanup
    mock_engine.dispose = AsyncMock()

    # Patch async_engine where it's imported and used (in lifespan.py)
    with patch("app.lifespan.async_engine", mock_engine):
        async with lifespan_manager.lifespan(app):
            assert hasattr(app.state, "async_engine")
            assert app.state.async_engine == mock_engine


@pytest.mark.asyncio
async def test_lifespan_cleanup_logs_shutdown(
    lifespan_manager: LifespanManager, mock_settings: Settings, mock_logger: MagicMock
):
    """
    Test that the lifespan shutdown logs the application shutdown message.

    Args:
        lifespan_manager (LifespanManager): The instance of LifespanManager used for testing.
        mock_settings (Settings): The mocked Settings instance.
        mock_logger (MagicMock): The mocked logger instance.
    """
    app = FastAPI()
    app.state.settings = mock_settings

    mock_engine = AsyncMock()
    # Mock the dispose method for cleanup
    mock_engine.dispose = AsyncMock()

    # Patch async_engine where it's imported and used (in lifespan.py)
    with patch("app.lifespan.async_engine", mock_engine):
        async with lifespan_manager.lifespan(app):
            pass

        # Verify that the shutdown message was logged
        mock_logger.info.assert_any_call("Application is shutting down...")
        # Verify that dispose was called during cleanup
        mock_engine.dispose.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_raises_exception_on_startup_failure(
    lifespan_manager: LifespanManager, mock_settings: Settings, mock_logger: MagicMock
):
    """
    Test that lifespan raises an exception if any resource initialization fails.

    Args:
        lifespan_manager (LifespanManager): The instance of LifespanManager used for testing.
        mock_settings (Settings): The mocked Settings instance.
        mock_logger (MagicMock): The mocked logger instance.
    """
    app = FastAPI()
    app.state.settings = mock_settings

    mock_engine = AsyncMock()
    mock_engine.dispose = AsyncMock()

    # Make logger.info raise an exception during startup to simulate a failure
    test_exception = Exception("Database initialization failed")
    mock_logger.info.side_effect = test_exception

    # Patch async_engine where it's imported and used (in lifespan.py)
    with patch("app.lifespan.async_engine", mock_engine):
        with pytest.raises(Exception, match="Database initialization failed"):
            async with lifespan_manager.lifespan(app):
                pass

        # Verify that dispose was still called in the finally block
        mock_engine.dispose.assert_called_once()
