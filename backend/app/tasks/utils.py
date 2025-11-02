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

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.db.base import AsyncSessionLocal

logger = logging.getLogger(__name__)


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
        AsyncSession instance for database operations.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database operation failed: {e}", exc_info=True)
            await session.rollback()
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
