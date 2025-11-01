"""
Utility functions for Celery tasks.

Provides helpers for async database operations, error handling, and task management.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import hashlib
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from config import Settings
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from psycopg_pool import ConnectionPool as SyncConnectionPool
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

logger = logging.getLogger(__name__)

# Global connection pool for Celery tasks
_db_pool: AsyncConnectionPool | None = None


def get_db_pool() -> AsyncConnectionPool:
    """Get or create database connection pool for Celery tasks.

    Returns:
        AsyncConnectionPool instance.

    Raises:
        RuntimeError: If database pool cannot be created.
    """
    global _db_pool

    if _db_pool is None:
        try:
            settings = Settings()
            database_url = settings.database_url

            # Create pool with open=False to avoid requiring event loop at creation time
            # The pool will be opened lazily when first used in an async context
            _db_pool = AsyncConnectionPool(
                conninfo=database_url,  # Use postgresql:// URL directly
                min_size=2,  # Minimum connections in pool
                max_size=10,  # Maximum connections in pool
                open=False,  # Don't open immediately - open lazily when first used
                timeout=30,  # Wait timeout for getting connection from pool
                max_waiting=10,  # Max clients waiting for connection
                kwargs={
                    "autocommit": True,
                    "row_factory": dict_row,  # Return rows as dicts
                },
            )

            logger.info(
                f"Database connection pool created for Celery tasks "
                f"(min={_db_pool.min_size}, max={_db_pool.max_size}, will open lazily)"
            )

        except Exception as e:
            logger.error(f"Failed to create database pool: {e}", exc_info=True)
            raise RuntimeError(f"Failed to create database pool: {e}") from e

    return _db_pool


def run_async(coro: Any) -> Any:
    """Run an async function in a sync context (for Celery tasks).

    Args:
        coro: Coroutine to execute.

    Returns:
        Result of the coroutine execution.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # If loop is already running, we're in an async context
        # This shouldn't happen in Celery, but handle it gracefully
        logger.warning("Event loop is already running, using asyncio.run()")
        return asyncio.run(coro)

    return loop.run_until_complete(coro)


@asynccontextmanager
async def get_db_context():
    """Async context manager for database operations in tasks.

    Yields:
        AsyncConnectionPool instance.
    """
    pool = get_db_pool()

    # Ensure pool is open - open it if closed (lazy opening)
    if pool.closed:
        logger.info("Opening database connection pool...")
        await pool.open()

    try:
        yield pool
    except Exception as e:
        logger.error(f"Database operation failed: {e}", exc_info=True)
        # Don't close the pool on error - let it handle reconnection
        raise


def calculate_file_hash(file_path: str | Path) -> str:
    """Calculate SHA256 hash of a file for deduplication.

    Args:
        file_path: Path to the file.

    Returns:
        Hexadecimal hash string.
    """
    sha256_hash = hashlib.sha256()
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


@retry(
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def retry_async_operation(operation: Any, *args: Any, **kwargs: Any) -> Any:
    """Retry an async operation with exponential backoff.

    Args:
        operation: Async function to retry.
        *args: Positional arguments for the operation.
        **kwargs: Keyword arguments for the operation.

    Returns:
        Result of the operation.

    Raises:
        Exception: If operation fails after all retries.
    """
    return await operation(*args, **kwargs)


def get_pdf_storage_path(company_id: int, fiscal_year: int, filename: str) -> Path:
    """Get storage path for a PDF document.

    Args:
        company_id: Company ID.
        fiscal_year: Fiscal year.
        filename: Original filename.

    Returns:
        Path object for storing the PDF.
    """
    base_path = Path("data/pdfs")
    company_path = base_path / f"company_{company_id}"
    year_path = company_path / str(fiscal_year)
    year_path.mkdir(parents=True, exist_ok=True)
    return year_path / filename


def validate_task_result(result: dict[str, Any], required_keys: list[str]) -> None:
    """Validate task result structure.

    Args:
        result: Task result dictionary.
        required_keys: List of required keys.

    Raises:
        ValueError: If required keys are missing.
    """
    missing_keys = [key for key in required_keys if key not in result]
    if missing_keys:
        raise ValueError(f"Task result missing required keys: {missing_keys}")
