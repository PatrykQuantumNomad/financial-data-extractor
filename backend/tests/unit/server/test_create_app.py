"""
Unit tests for the `__init__.py` module of the `src.app` package.

This module tests the `create_app` factory function, ensuring that it correctly
initializes and configures the FastAPI application with all necessary components,
including logging, settings, metrics, error handling, routes, and middleware.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from unittest.mock import MagicMock

import pytest
from app import create_app
from fastapi import FastAPI
from pytest_mock import MockerFixture


@pytest.fixture(name="mock_logger")
def fixture_mock_logger(mocker: MockerFixture) -> MagicMock:
    """
    Fixture to mock the AppLogger class.

    This ensures that logging initialization does not interfere with tests
    and allows assertions on logger method calls.

    Returns:
        MagicMock: The mocked AppLogger class.
    """
    mock_logger_class = mocker.patch("app.AppLogger")
    return mock_logger_class


@pytest.fixture(name="mock_settings")
def fixture_mock_settings(mocker: MockerFixture) -> MagicMock:
    """
    Fixture to mock the Settings class.

    This provides a mocked Settings instance with predefined attribute values
    to bypass pydantic validation and control configuration within tests.

    Returns:
        MagicMock: The mocked Settings instance.
    """
    mock_settings_class = mocker.patch("app.Settings")
    mock_settings_instance = mock_settings_class.return_value

    # Set required attributes with test values
    mock_settings_instance.langchain_project = "test_project"
    mock_settings_instance.langchain_tracing_v2 = "false"
    mock_settings_instance.langchain_endpoint = "http://test-endpoint"
    mock_settings_instance.langchain_api_key = "test_api_key"
    mock_settings_instance.app_log_level = "DEBUG"
    mock_settings_instance.logging_path = "logging.json"
    mock_settings_instance.cors_allowed_origins = ["https://example.com"]

    return mock_settings_instance


@pytest.fixture(name="mock_builder")
def fixture_mock_builder(mocker: MockerFixture) -> tuple[MagicMock, MagicMock, MagicMock]:
    """
    Fixture to mock the FastAPIAppBuilder class.

    This ensures that the builder's methods can be controlled and monitored
    without executing the actual implementation.

    Returns:
        Tuple[MagicMock, MagicMock, MagicMock]:
            - The first MagicMock mocks the FastAPIAppBuilder class.
            - The second MagicMock mocks the FastAPIAppBuilder instance.
            - The third MagicMock mocks the FastAPI application returned by the builder's build method.
    """
    mock_builder_class = mocker.patch("app.FastAPIAppBuilder")
    mock_builder_instance = MagicMock()

    # Configure the builder instance to return itself on setup method calls for method chaining
    mock_builder_instance.setup_settings.return_value = mock_builder_instance
    mock_builder_instance.setup_logging.return_value = mock_builder_instance
    mock_builder_instance.setup_metrics.return_value = mock_builder_instance
    mock_builder_instance.setup_error_handlers.return_value = mock_builder_instance
    mock_builder_instance.setup_api_routes.return_value = mock_builder_instance
    mock_builder_instance.setup_routes.return_value = mock_builder_instance
    mock_builder_instance.setup_middleware.return_value = mock_builder_instance

    # Mock the FastAPI application returned by the builder's build method
    mock_app = MagicMock(spec=FastAPI)
    mock_builder_instance.build.return_value = mock_app

    # Assign the mock builder instance to the builder class
    mock_builder_class.return_value = mock_builder_instance

    return mock_builder_class, mock_builder_instance, mock_app


def test_create_app_success(
    mock_logger: MagicMock,
    mock_builder: tuple[MagicMock, MagicMock, MagicMock],
    mock_settings: MagicMock,
):
    """
    Test that `create_app` successfully creates the FastAPI application with all components.

    This test verifies that the `create_app` function initializes the AppLogger,
    instantiates FastAPIAppBuilder with the correct settings and logger, calls all
    necessary setup methods exactly once, builds the FastAPI app, and returns it.

    Args:
        mock_logger (MagicMock): The mocked AppLogger class.
        mock_builder (tuple): The mocked FastAPIAppBuilder instance and FastAPI app.
        mock_settings (MagicMock): The mocked Settings instance.
    """
    mock_builder_class, mock_builder_instance, mock_app = mock_builder

    # Call the function under test
    app = create_app()

    # Assertions
    mock_logger.initialize_logger.assert_called_once()
    mock_builder_class.assert_called_once_with(settings=mock_settings, logger=mock_logger.logger)
    mock_builder_instance.setup_settings.assert_called_once()
    mock_builder_instance.setup_logging.assert_called_once()
    mock_builder_instance.setup_metrics.assert_called_once()
    mock_builder_instance.setup_error_handlers.assert_called_once()
    mock_builder_instance.setup_api_routes.assert_called_once()
    mock_builder_instance.setup_routes.assert_called_once()
    mock_builder_instance.setup_middleware.assert_called_once()
    mock_builder_instance.build.assert_called_once()

    # Verify that the app returned by create_app() is the mocked FastAPI app
    assert app == mock_app


def test_create_app_logger_initialization_failure(
    mocker: MockerFixture,
    mock_builder: tuple[MagicMock, MagicMock, MagicMock],
):
    """
    Test that `create_app` propagates exceptions raised by `AppLogger.initialize_logger`.

    This ensures that the application does not start if logging fails to initialize.

    Args:
        mocker (MockerFixture): The pytest-mock fixture for mocking dependencies.
        mock_builder (Tuple[MagicMock, MagicMock, MagicMock]): The mocked FastAPIAppBuilder class,
          instance, and FastAPI app.
    """
    # Mock AppLogger to raise an exception during initialization
    mock_logger_class = mocker.patch("app.AppLogger")
    mock_logger_class.initialize_logger.side_effect = Exception("Logger initialization failed")

    # Mock FastAPIAppBuilder class to ensure it's not instantiated
    mock_builder_class, _, _ = mock_builder

    # Call the function under test and verify that it raises the exception
    with pytest.raises(Exception) as exc_info:
        create_app()

    assert str(exc_info.value) == "Logger initialization failed"

    # Verify that FastAPIAppBuilder was never instantiated
    mock_builder_class.assert_not_called()


def test_create_app_builder_setup_failure(
    mock_builder: tuple[MagicMock, MagicMock, MagicMock],
    mock_settings: MagicMock,
):
    """
    Test that `create_app` propagates exceptions raised during FastAPIAppBuilder setup.

    This ensures that the application does not start if any setup step fails.

    Args:
        mock_builder (Tuple[MagicMock, MagicMock, MagicMock]): The mocked FastAPIAppBuilder class,
          instance, and FastAPI app.
        mock_settings (MagicMock): The mocked Settings instance.
    """
    _, mock_builder_instance, _ = mock_builder

    # Configure the builder instance to raise an exception during setup_metrics
    mock_builder_instance.setup_metrics.side_effect = Exception("Metrics setup failed")

    # Call the function under test and verify that it raises the exception
    with pytest.raises(Exception) as exc_info:
        create_app()

    assert str(exc_info.value) == "Metrics setup failed"

    # Verify that setup_settings and setup_logging were called before the failure
    mock_builder_instance.setup_settings.assert_called_once()
    mock_builder_instance.setup_logging.assert_called_once()

    # Verify that setup_metrics was called and failed
    mock_builder_instance.setup_metrics.assert_called_once()

    # Verify that subsequent setup methods were not called
    mock_builder_instance.setup_error_handlers.assert_not_called()
    mock_builder_instance.setup_api_routes.assert_not_called()
    mock_builder_instance.setup_routes.assert_not_called()
    mock_builder_instance.setup_route_integration.assert_not_called()
    mock_builder_instance.setup_middleware.assert_not_called()
    mock_builder_instance.build.assert_not_called()
