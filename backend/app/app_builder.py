"""
This module provides a builder class for configuring and constructing a FastAPI application.

It allows the configuration of various components like settings, logging, metrics, error handlers,
routes, middleware, and external service integrations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
import logging.config
import os
import platform
from typing import Any

from app.api.middleware.fastapi_error_handler import ErrorHandler
from config import Settings
from fastapi import FastAPI, Request
from fastapi import __version__ as fastapi_version
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from prometheus_client import Info
from starlette_exporter import PrometheusMiddleware, handle_metrics
from starlette_exporter.optional_metrics import (request_body_size,
                                                 response_body_size)

from .api.middleware.request_context import (RequestIDMiddleware,
                                             TimeoutMiddleware)
from .lifespan import LifespanManager
from .utils.file_utils import load_json_file
from .utils.log_filter import SuppressSpecificLogEntries
from .utils.logger import AppLogger

# Prometheus metric to track FastAPI app information (app_name, python_version, etc.)
INFO = Info("fastapi_app_info", "FastAPI application information.")


class FastAPIAppBuilder:
    """Builder class to configure and construct a FastAPI application.

    This class provides methods to set up various components of a FastAPI application,
    such as settings, logging, metrics, error handlers, routes, and middleware.
    """

    def __init__(self, settings: Settings | None = None, logger: logging.Logger | None = None):
        """Initializes a new instance of FastAPIAppBuilder.

        Args:
            settings (Optional[Settings]): Configuration settings for the application.
                If None, defaults to loading from environment variables.
            logger (Optional[logging.Logger]): Logger instance. If None, a default logger is used.
        """
        self.logger = logger or AppLogger.get_logger()
        self.settings = settings or Settings()  # type: ignore

        # Some libs require env vars
        self._set_environment_variables()

        self.fast_api = FastAPI(lifespan=LifespanManager(self.settings, self.logger).lifespan)

    def _set_environment_variables(self) -> None:
        """Set the required environment variables for external dependencies
        based on the settings."""
        env_vars = {}

        for key, value in env_vars.items():
            os.environ[key] = value

    def setup_settings(self) -> "FastAPIAppBuilder":
        """Initializes and loads application settings.

        This method assigns configuration settings from the environment or
        configuration file to the FastAPI application instance.

        Returns:
            FastAPIAppBuilder: The instance of the builder (self).
        """
        self.fast_api.state.settings = self.settings
        return self

    def setup_logging(self) -> "FastAPIAppBuilder":
        """Sets up logging configurations for the FastAPI application.

        This method loads the logging configuration from a JSON file specified
        in the application settings and applies it. It also configures
        the log level and sets up specific log filtering for certain endpoints.

        Returns:
            FastAPIAppBuilder: The instance of the builder (self).
        """

        try:
            # Load the logging configuration from JSON file
            logging_config: dict[str, Any] = load_json_file(self.settings.logging_path)

            # Apply the logging configuration
            logging.config.dictConfig(logging_config)

            # Set the log level on the passed logger and its handlers
            log_level = self.settings.app_log_level.upper()
            self.logger.setLevel(log_level)
            for handler in self.logger.handlers:
                handler.setLevel(log_level)

            # Suppress logging for specific endpoints, e.g., /metrics to reduce log noise
            endpoints_to_suppress = ["/metrics"]
            uvicorn_access_logger = logging.getLogger("uvicorn.access")
            uvicorn_access_logger.addFilter(SuppressSpecificLogEntries(endpoints_to_suppress))

            self.logger.info("Logging has been configured successfully.")
        except Exception as e:
            self.logger.exception("Failed to set up logging: %s", e)
            raise
        return self

    def setup_metrics(self) -> "FastAPIAppBuilder":
        """Sets up Prometheus middleware for collecting application metrics.

        This method configures Prometheus metrics, including request/response sizes,
        and excludes certain paths and methods from metrics collection.

        Returns:
            FastAPIAppBuilder: The instance of the builder (self).
        """
        try:
            settings: Settings = self.settings

            # Track FastAPI app version and Python/fastapi version via Prometheus
            INFO.info(
                {
                    "app_name": settings.app_name,
                    "python_version": platform.python_version(),
                    "fastapi_version": fastapi_version,
                    "app_version": settings.app_version,
                }
            )

            # Add Prometheus middleware with optional request/response size tracking
            self.fast_api.add_middleware(
                PrometheusMiddleware,
                group_paths=False,
                prefix="http",
                app_name=settings.app_name,
                optional_metrics=[response_body_size, request_body_size],
                skip_paths=["/healthcheck"],
                skip_methods=["OPTIONS"],
            )

            # Expose the /metrics endpoint for Prometheus scraping
            self.fast_api.add_route("/metrics", handle_metrics)

            self.logger.info("Prometheus metrics have been set up successfully.")
        except Exception as e:
            self.logger.exception("Failed to set up Prometheus metrics: %s", e)
            raise
        return self

    def setup_error_handlers(self) -> "FastAPIAppBuilder":
        """Configures the global error handlers for the application.

        This method registers custom error handlers to provide meaningful and
        user-friendly responses in case of exceptions during request processing.

        Returns:
            FastAPIAppBuilder: The instance of the builder (self).
        """
        try:
            error_handler = ErrorHandler(self.fast_api, self.logger)
            error_handler.register_default_handlers()
            self.logger.info("Error handlers have been registered successfully.")
        except Exception as e:
            self.logger.exception("Failed to set up error handlers: %s", e)
            raise

        return self

    def setup_api_routes(self) -> "FastAPIAppBuilder":
        """Registers the API routes for the FastAPI application.

        This method includes the API v1 router with all business endpoints
        (companies, documents, extractions, compiled statements).

        Returns:
            FastAPIAppBuilder: The instance of the builder (self).
        """
        # Include API v1 router with all business endpoints
        from app.api.v1 import api_router

        self.fast_api.include_router(api_router)

        self.logger.info("API v1 routes have been registered successfully.")
        return self

    def setup_routes(self) -> "FastAPIAppBuilder":
        """Defines and registers the general routes for the FastAPI application.

        This method adds basic routes such as a health check endpoint, a root endpoint,
        and an endpoint for listing all routes available in the application.

        Returns:
            FastAPIAppBuilder: The instance of the builder (self).
        """

        @self.fast_api.get("/healthcheck", tags=["Health"])
        async def health_check():
            """Endpoint for health checking the application."""
            return {"status": "Healthy"}

        @self.fast_api.get("/", response_class=HTMLResponse, tags=["Root"])
        async def root():
            """Root endpoint that returns a welcome HTML page."""
            html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Welcome</title>
                </head>
                <body>
                    <h1>Welcome to the Financial Data Extractor API!</h1>
                </body>
                </html>
                """
            return HTMLResponse(content=html_content)

        @self.fast_api.get("/endpoints/", response_class=JSONResponse, tags=["Utility"])
        async def endpoints(request: Request):
            """
            Endpoint to list all available routes in the application.

            Args:
                request (Request): The incoming HTTP request.

            Returns:
                JSONResponse: A list of all routes available in the application.
            """
            endpoints: list[dict[str, str | list[str]]] = [
                {"path": route.path, "name": route.name, "methods": list(route.methods)}
                for route in request.app.routes
                if hasattr(route, "path")
            ]

            # Use jsonable_encoder to ensure the data is properly serialized
            formatted_response = jsonable_encoder({"endpoints": endpoints})

            # Return the JSONResponse with the formatted data
            return JSONResponse(content=formatted_response)

        self.logger.info("General routes have been set up successfully.")
        return self

    def setup_middleware(self) -> "FastAPIAppBuilder":
        """Sets up middleware for the FastAPI application, including CORS, request ID,
        and timeout handling.

        This method configures the middleware necessary for CORS, unique request ID generation,
        and timeout enforcement.

        Returns:
            FastAPIAppBuilder: The instance of the builder (self).
        """
        try:
            # Add TimeoutMiddleware with a timeout
            self.fast_api.add_middleware(TimeoutMiddleware, timeout=self.settings.request_timeout)

            # Add request ID middleware
            self.fast_api.add_middleware(RequestIDMiddleware)

            # Set all CORS enabled origins
            self.fast_api.add_middleware(
                CORSMiddleware,
                allow_origins=self.settings.cors_allowed_origins,
                allow_credentials=True,
                allow_methods=["*"],  # Allow all HTTP methods
                allow_headers=["*"],  # Allow all headers
                expose_headers=["*"],  # Expose all headers
            )

            self.logger.info("Additional middleware has been set up successfully.")
        except Exception as e:
            self.logger.exception("Failed to set up middleware: %s", e)
            raise

        return self

    def build(self) -> FastAPI:
        """Finalizes the application configuration and returns the FastAPI instance.

        Returns:
            FastAPI: The fully configured FastAPI application.
        """
        self.logger.info("FastAPI application has been built successfully.")
        return self.fast_api
