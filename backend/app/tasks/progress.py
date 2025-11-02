"""
Progress callback for Celery tasks.

Bridges worker progress updates to Celery task state updates.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from celery import Task

from app.workers.base import ProgressCallback


class CeleryProgressCallback(ProgressCallback):
    """Progress callback that updates Celery task state."""

    def __init__(self, celery_task: Task):
        """Initialize callback with Celery task.

        Args:
            celery_task: Celery task instance.
        """
        self.celery_task = celery_task

    def update(self, step: str, meta: dict[str, Any] | None = None) -> None:
        """Update Celery task state with progress.

        Args:
            step: Current step name.
            meta: Optional metadata dictionary.
        """
        state_meta = {"step": step}
        if meta:
            state_meta.update(meta)
        self.celery_task.update_state(state="PROGRESS", meta=state_meta)
