"""
This module manages the lifespan of the FastAPI application.

It initializes and cleans up essential resources such as the database connection pool.
Ensures proper cleanup of resources upon application startup and shutdown.

Author: Patryk Golabek
Company: Translucent Computing Inc.
Copyright: 2024 Translucent Computing Inc.
"""

import logging
import logging.config
from contextlib import asynccontextmanager
from urllib.parse import quote_plus

from config import Settings
from fastapi import FastAPI
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


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

        This context manager initializes the database connection pool
        and ensures proper cleanup of resources upon application shutdown.

        Args:
            app (FastAPI): The FastAPI application instance.

        Yields:
            None: Hands control back to the application.
        """
        try:
            settings: Settings = app.state.settings

            # URL-encode the database credentials to handle special characters
            db_username = quote_plus(settings.db_username)
            db_password = quote_plus(settings.db_password)

            # Construct the database URI from settings
            db_uri = (
                f"postgresql://{db_username}:{db_password}"
                f"@{settings.db_host}:{settings.db_port}/"
                f"{settings.db_name}"
            )

            # Create the connection pool using async with
            async with AsyncConnectionPool(
                conninfo=db_uri, max_size=20, kwargs={"autocommit": True, "row_factory": dict_row}
            ) as pool:
                app.state.db_pool = pool
                self.logger.info("Database connection pool created successfully.")
                # Yield control to the application to start processing
                yield

        except Exception as e:
            self.logger.exception("Failed during application lifespan initialization: %s", e)
            raise
        finally:
            self.logger.info("Application is shutting down...")
