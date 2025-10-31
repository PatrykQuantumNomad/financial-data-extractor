"""
This module provides a factory method to create and configure an instance of the
FastAPI application, complete with logging, routes, error handling, CORS, and middleware.

The goal of this module is to provide a fully-configured, ready-to-deploy FastAPI application
that includes Prometheus metrics collection, error handling, and request management.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging

from config import Settings
from fastapi import FastAPI

from .app_builder import FastAPIAppBuilder
from .utils.logger import AppLogger


def create_app() -> FastAPI:
    """
    Factory method to create, configure, and return an instance of the FastAPI application.

    The method sets up the application with logging, error handling, routing, middleware,
    and external service integrations, ensuring the app is ready for deployment.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    # Initialize and configure the AppLogger before passing it to the builder
    AppLogger.initialize_logger(log_level=logging.INFO)

    builder = FastAPIAppBuilder(settings=Settings(), logger=AppLogger.logger)
    app = (
        builder.setup_settings()  # Initialize settings
        .setup_logging()  # Configure logging
        .setup_metrics()  # Setup Prometheus metrics
        .setup_error_handlers()  # Configure error handlers
        .setup_routes()  # Define basic routes
        .setup_middleware()  # Configure middleware
        .build()
    )
    return app
