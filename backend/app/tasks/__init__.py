"""
Celery tasks for financial data extraction and processing.

This module exports the Celery app instance and task decorators.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from app.tasks.celery_app import celery_app

__all__ = ["celery_app"]
