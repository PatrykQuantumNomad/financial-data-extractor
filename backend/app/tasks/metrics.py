"""
Prometheus metrics for Celery tasks.

Exposes metrics for task execution, duration, failures, and queue depth.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import time
from typing import Any

from celery import Task
from celery.signals import task_failure, task_postrun, task_prerun, task_success, worker_ready
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Task metrics
task_duration = Histogram(
    "celery_task_duration_seconds",
    "Time spent executing Celery tasks",
    ["task_name", "queue"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, float("inf")),
)

task_total = Counter(
    "celery_tasks_total",
    "Total number of Celery tasks",
    ["task_name", "state", "queue"],
)

task_active = Gauge("celery_tasks_active", "Number of active Celery tasks", ["task_name", "queue"])

queue_length = Gauge("celery_queue_length", "Number of tasks in queue", ["queue"])

# Track task start times for duration calculation
_task_start_times: dict[str, float] = {}


@worker_ready.connect
def setup_metrics_server(sender: Any, **kwargs: Any) -> None:
    """Start Prometheus metrics HTTP server when worker is ready.

    The server will listen on port 9091 by default for Prometheus scraping.
    """
    import logging

    logger = logging.getLogger(__name__)
    try:
        # Start HTTP server on a non-conflicting port
        # This will be exposed if running in Docker or accessible from host
        start_http_server(9091)
        logger.info("Prometheus metrics server started on port 9091")
    except OSError:
        # Port might already be in use (e.g., multiple workers)
        logger.warning("Prometheus metrics server port 9091 already in use, skipping")


@task_prerun.connect
def task_prerun_handler(sender: Task, task_id: str, **kwargs: Any) -> None:
    """Record task start time and increment active tasks."""
    task_name = sender.name
    queue = getattr(sender.request, "delivery_info", {}).get("routing_key", "unknown")
    _task_start_times[task_id] = time.time()
    task_active.labels(task_name=task_name, queue=queue).inc()


@task_postrun.connect
def task_postrun_handler(sender: Task, task_id: str, state: str, **kwargs: Any) -> None:
    """Record task duration and decrement active tasks."""
    task_name = sender.name
    queue = getattr(sender.request, "delivery_info", {}).get("routing_key", "unknown")

    # Calculate duration
    start_time = _task_start_times.pop(task_id, None)
    if start_time:
        duration = time.time() - start_time
        task_duration.labels(task_name=task_name, queue=queue).observe(duration)

    # Decrement active tasks
    task_active.labels(task_name=task_name, queue=queue).dec()


@task_success.connect
def task_success_handler(sender: Task, **kwargs: Any) -> None:
    """Increment success counter."""
    task_name = sender.name
    queue = getattr(sender.request, "delivery_info", {}).get("routing_key", "unknown")
    task_total.labels(task_name=task_name, state="SUCCESS", queue=queue).inc()


@task_failure.connect
def task_failure_handler(sender: Task, **kwargs: Any) -> None:
    """Increment failure counter."""
    task_name = sender.name
    queue = getattr(sender.request, "delivery_info", {}).get("routing_key", "unknown")
    task_total.labels(task_name=task_name, state="FAILURE", queue=queue).inc()


# Note: Queue length metrics would require accessing Redis directly
# This is best done via a separate exporter or periodic task
# For now, Flower or Redis exporter can provide queue metrics
