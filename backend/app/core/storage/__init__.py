"""
Storage service for object storage (MinIO/S3).

Provides unified interface for storing and retrieving PDF documents
from object storage or local file system.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from app.core.storage.storage_service import (
    IStorageService,
    StorageService,
    StorageServiceConfig,
    create_storage_service,
)

__all__ = [
    "IStorageService",
    "StorageService",
    "StorageServiceConfig",
    "create_storage_service",
]
