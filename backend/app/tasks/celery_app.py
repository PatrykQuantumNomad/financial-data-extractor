"""
Celery application configuration.

Configures Celery with Redis as broker and result backend.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import os
import platform
from typing import Any

from celery import Celery
from celery.signals import setup_logging, worker_ready

from config import Settings

# Get settings instance
try:
    settings = Settings()
except Exception:
    # Fallback for Celery worker initialization when .env might not be loaded
    settings = None

# Redis broker URL
REDIS_HOST = os.getenv("REDIS_HOST", settings.redis_host if settings else "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", str(settings.redis_port) if settings else "6379")
REDIS_DB = os.getenv("REDIS_DB", str(settings.redis_db) if settings else "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", settings.redis_password if settings else "")

# Build Redis URL
if REDIS_PASSWORD:
    redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Create Celery app instance
celery_app = Celery(
    "financial-data-extractor",
    broker=redis_url,
    backend=redis_url,
    include=[
        "app.tasks.scraping_tasks",
        "app.tasks.extraction_tasks",
        "app.tasks.compilation_tasks",
        "app.tasks.orchestration_tasks",
    ],
)

# Determine worker pool based on platform
# macOS has issues with prefork pool due to Objective-C runtime
# Use threads pool on macOS, prefork on Linux
IS_MACOS = platform.system() == "Darwin"
WORKER_POOL = "threads" if IS_MACOS else "prefork"

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # Disable prefetching for better load balancing
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks to prevent memory leaks
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    result_expires=3600,  # Results expire after 1 hour
    # Store task results in backend (required for Flower to show task history)
    task_ignore_result=False,
    # Use threads pool on macOS to avoid fork issues
    worker_pool=WORKER_POOL,
    # Task routing
    task_routes={
        "app.tasks.scraping_tasks.*": {"queue": "scraping"},
        "app.tasks.extraction_tasks.*": {"queue": "extraction"},
        "app.tasks.compilation_tasks.*": {"queue": "compilation"},
        "app.tasks.orchestration_tasks.*": {"queue": "orchestration"},
    },
    # Task-specific settings
    task_default_queue="default",
    task_default_exchange="tasks",
    task_default_exchange_type="direct",
    task_default_routing_key="default",
)


@setup_logging.connect
def config_loggers(*args: Any, **kwargs: Any) -> None:
    """Configure logging for Celery workers."""
    import logging
    import sys

    # Configure logging for Celery workers
    # Set up console handler for task logs
    root_logger = logging.getLogger()

    # Remove any existing handlers
    root_logger.handlers.clear()

    # Create console handler with readable format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Use simple format for Celery worker output (not JSON)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    # Configure loggers for tasks
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Set specific loggers for task modules
    task_loggers = [
        "app.tasks",
        "app.tasks.scraping_tasks",
        "app.tasks.extraction_tasks",
        "app.tasks.compilation_tasks",
        "app.tasks.orchestration_tasks",
        "app.tasks.utils",
    ]

    for logger_name in task_loggers:
        task_logger = logging.getLogger(logger_name)
        task_logger.setLevel(logging.INFO)
        task_logger.addHandler(console_handler)
        task_logger.propagate = False  # Don't propagate to root to avoid duplicate logs

    # Also configure celery and kombu loggers
    celery_logger = logging.getLogger("celery")
    celery_logger.setLevel(logging.INFO)
    celery_logger.addHandler(console_handler)

    kombu_logger = logging.getLogger("kombu")
    kombu_logger.setLevel(logging.WARNING)  # Reduce kombu verbosity


@worker_ready.connect
def init_db_session(*args: Any, **kwargs: Any) -> None:
    """Initialize database session factory when worker starts.

    With SQLAlchemy async sessions, the session factory is already initialized
    via AsyncSessionLocal. This function logs initialization for monitoring.
    """
    import logging

    logger = logging.getLogger(__name__)
    try:
        # AsyncSessionLocal is already initialized in app.db.base
        # No need to pre-warm since sessions are created on-demand
        logger.info("Database async session factory ready for Celery worker")

        # Test that we can create a session (optional, for validation)
        async def test_session():
            try:
                from sqlalchemy import text

                from app.db.base import AsyncSessionLocal

                # Create a test session and execute a simple query
                async with AsyncSessionLocal() as session:
                    await session.execute(text("SELECT 1"))
                    logger.info("Database session factory validated successfully")
            except Exception as e:
                logger.warning(f"Could not validate database session: {e}")

        # Run the test in a new event loop
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, schedule the test
                asyncio.create_task(test_session())
            else:
                loop.run_until_complete(test_session())
        except RuntimeError:
            # No event loop, create one
            asyncio.run(test_session())

    except Exception as e:
        logger.error(f"Failed to initialize database session factory: {e}", exc_info=True)
        # Don't raise - let tasks handle the error when they try to use it


if __name__ == "__main__":
    celery_app.start()
