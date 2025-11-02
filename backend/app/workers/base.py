"""
Base worker class for business logic.

All workers inherit from this base class which provides common
functionality and interfaces for testing.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class ProgressCallback:
    """Callback interface for task progress updates.

    Allows workers to report progress without being tied to Celery.
    """

    def update(self, step: str, meta: dict[str, Any] | None = None) -> None:
        """Update progress with step name and optional metadata.

        Args:
            step: Current step name.
            meta: Optional metadata dictionary.
        """
        # Default implementation does nothing
        # Subclasses can override to handle progress updates
        pass


class NoOpProgressCallback(ProgressCallback):
    """Progress callback that does nothing (for testing)."""

    pass


class BaseWorker(ABC):
    """Base class for all workers.

    Workers encapsulate business logic and can be tested independently
    from Celery. They accept dependencies via constructor and use
    a progress callback for status updates.

    Attributes:
        progress_callback: Callback for progress updates.
        logger: Logger instance for this worker.
    """

    def __init__(self, progress_callback: ProgressCallback | None = None):
        """Initialize worker.

        Args:
            progress_callback: Optional callback for progress updates.
                Defaults to NoOpProgressCallback if not provided.
        """
        self.progress_callback = progress_callback or NoOpProgressCallback()
        self.logger = logging.getLogger(self.__class__.__name__)

    def update_progress(self, step: str, meta: dict[str, Any] | None = None) -> None:
        """Update progress via callback.

        Args:
            step: Current step name.
            meta: Optional metadata dictionary.
        """
        self.progress_callback.update(step, meta)

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute the worker's main business logic.

        This method contains the core business logic that can be
        tested independently.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Dictionary with execution results.

        Raises:
            Exception: If execution fails.
        """
        pass
