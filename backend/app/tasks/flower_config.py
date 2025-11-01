"""
Flower configuration for Celery monitoring dashboard.

Flower provides a web-based tool for monitoring Celery clusters and tasks.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

# Flower configuration can be passed via command line or environment variables
# Common options:
#   --port=5555              : Port to run Flower on (default: 5555)
#   --broker=redis://...     : Redis broker URL
#   --broker_api=redis://...  : Redis API URL for broker monitoring
#   --basic_auth=user:pass   : Basic authentication
#   --url_prefix=/flower      : URL prefix (useful when behind reverse proxy)

# Example Flower startup:
# celery -A app.tasks.celery_app flower --port=5555 --broker=redis://localhost:6379/0

# For production, consider adding:
#   --basic_auth=admin:secure_password
#   --url_prefix=/flower
#   --persistent=True

__all__ = []
