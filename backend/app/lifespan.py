"""
This module manages the lifespan of the FastAPI application.

It initializes and cleans up essential resources such as the database async engine.
Ensures proper cleanup of resources upon application startup and shutdown.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import async_engine
from config import Settings


class LifespanManager:
    """
    Class to manage the lifespan of the FastAPI application.

    This class handles resource initialization and cleanup during the startup
    and shutdown phases of the application lifecycle.
    """

    def __init__(self, settings: Settings, logger: logging.Logger):
        """
        Initializes a new instance of LifespanManager.

        Args:
            settings (Settings): Configuration settings for the application.
            logger (logging.Logger): Logger instance for logging operations.
        """
        self.logger = logger
        self.settings = settings

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """
        Lifespan event handler to initialize and cleanup resources.

        This context manager stores the async database engine in app state
        and ensures proper cleanup of resources upon application shutdown.

        Args:
            app (FastAPI): The FastAPI application instance.

        Yields:
            None: Hands control back to the application.
        """
        try:
            # Store the async engine in app state for repository access
            app.state.async_engine = async_engine
            self.logger.info("Database async engine initialized successfully.")

            # Yield control to the application to start processing
            yield

        except Exception as e:
            self.logger.exception("Failed during application lifespan initialization: %s", e)
            raise
        finally:
            # Cleanup async engine
            await async_engine.dispose()
            self.logger.info("Application is shutting down...")
