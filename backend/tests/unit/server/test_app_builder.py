"""
Unit tests for the `app_builder.py` module of the `app` package.

This module tests the `FastAPIAppBuilder` class, ensuring that it correctly
configures and constructs a FastAPI application with all necessary components,
including settings, logging, metrics, error handlers, routes, and middleware.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pytest_mock import MockerFixture

from app.api.middleware.request_context import RequestIDMiddleware, TimeoutMiddleware
from app.app_builder import FastAPIAppBuilder


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
    mock_settings_instance.request_timeout = 10  # Add missing attributes as needed
    mock_settings_instance.app_name = "test_app"
    mock_settings_instance.app_version = "1.0.0"

    return mock_settings_instance


@pytest.fixture(name="app_builder")
def fixture_app_builder(mock_settings: MagicMock) -> FastAPIAppBuilder:
    """
    Fixture to create an instance of FastAPIAppBuilder with a mocked settings instance.

    Returns:
        FastAPIAppBuilder: The instance of FastAPIAppBuilder.
    """
    logger = MagicMock()
    return FastAPIAppBuilder(settings=mock_settings, logger=logger)


def test_setup_settings(app_builder: FastAPIAppBuilder):
    """
    Test that setup_settings correctly assigns settings to the FastAPI app instance.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
    """
    # Call the method under test
    app_builder.setup_settings()

    # Verify that settings are assigned to the FastAPI app state
    assert app_builder.fast_api.state.settings == app_builder.settings


def test_setup_logging(app_builder: FastAPIAppBuilder, mocker: MockerFixture):
    """
    Test that setup_logging configures the logger correctly and applies logging filters.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
        mocker (MockerFixture): The pytest-mock fixture for mocking dependencies.
    """
    # Mock load_json_file to return a sample logging config
    mock_logging_config = {"version": 1, "disable_existing_loggers": False}
    mocker.patch("app.app_builder.load_json_file", return_value=mock_logging_config)
    mock_dict_config = mocker.patch("logging.config.dictConfig")

    # Call the method under test
    app_builder.setup_logging()

    # Verify that logging configuration was applied
    mock_dict_config.assert_called_once_with(mock_logging_config)
    app_builder.logger.setLevel.assert_called_once_with(app_builder.settings.app_log_level.upper())


def test_setup_metrics(app_builder: FastAPIAppBuilder):
    """
    Test that setup_metrics adds Prometheus middleware and metrics route.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
    """
    # Call the method under test
    app_builder.setup_metrics()

    # Verify that middleware and /metrics route are added
    assert any(
        middleware.cls.__name__ == "PrometheusMiddleware"
        for middleware in app_builder.fast_api.user_middleware
    )
    assert any(route.path == "/metrics" for route in app_builder.fast_api.routes)


def test_setup_error_handlers(app_builder: FastAPIAppBuilder, mocker: MockerFixture):
    """
    Test that setup_error_handlers registers error handlers correctly.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
        mocker (MockerFixture): The pytest-mock fixture for mocking dependencies.
    """
    # Mock ErrorHandler
    mock_error_handler = mocker.patch("app.app_builder.ErrorHandler")
    mock_error_handler_instance = mock_error_handler.return_value

    # Call the method under test
    app_builder.setup_error_handlers()

    # Verify that error handlers were registered
    mock_error_handler_instance.register_default_handlers.assert_called_once()


def test_setup_routes(app_builder: FastAPIAppBuilder):
    """
    Test that setup_routes adds default routes like health check, root, and endpoints.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
    """
    # Call the method under test
    app_builder.setup_routes()

    # Verify that the health check, root, and endpoints routes are added
    assert any(route.path == "/healthcheck" for route in app_builder.fast_api.routes)
    assert any(route.path == "/" for route in app_builder.fast_api.routes)
    assert any(route.path == "/endpoints/" for route in app_builder.fast_api.routes)

def test_setup_middleware(app_builder: FastAPIAppBuilder):
    """
    Test that setup_middleware adds TimeoutMiddleware, RequestIDMiddleware, and CORS middleware.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
    """
    # Call the method under test
    app_builder.setup_middleware()

    # Verify that middleware is added
    middleware_classes = [middleware.cls for middleware in app_builder.fast_api.user_middleware]
    assert TimeoutMiddleware in middleware_classes
    assert RequestIDMiddleware in middleware_classes
    assert CORSMiddleware in middleware_classes


def test_build(app_builder: FastAPIAppBuilder):
    """
    Test that build returns the fully configured FastAPI app.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
    """
    # Call the method under test
    app = app_builder.build()

    # Verify that the returned app is the FastAPI instance
    assert isinstance(app, FastAPI)


def test_complete_app_setup(app_builder: FastAPIAppBuilder):
    """
    Test that the entire application can be set up using all setup methods sequentially.

    Args:
        app_builder (FastAPIAppBuilder): The builder instance used for testing.
    """
    # Set up the complete application
    (
        app_builder.setup_settings()
        .setup_logging()
        .setup_metrics()
        .setup_error_handlers()
        .setup_routes()
        .setup_middleware()
    )

    # Build the final app
    app = app_builder.build()

    # Verify that the app is correctly configured
    assert isinstance(app, FastAPI)

    # /metrics is registered as a Starlette route by PrometheusMiddleware
    has_metrics = False
    for route in app.routes:
        # For FastAPI, a route may be APIRoute or Mount with subroutes
        if getattr(route, "path", None) == "/metrics":
            has_metrics = True
            break
        # In some configs, Prometheus endpoint might use route.name
        if getattr(route, "name", None) == "handle_metrics":
            has_metrics = True
            break

    assert has_metrics, "The /metrics Prometheus route was not registered"
    assert getattr(app.state, "settings", None) == app_builder.settings
