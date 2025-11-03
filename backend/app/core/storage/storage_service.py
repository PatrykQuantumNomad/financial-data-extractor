"""
Unified storage service for PDF documents.

Supports both MinIO/S3 object storage and local file system storage
with automatic fallback and migration support.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import hashlib
import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path

from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class StorageServiceConfig(BaseModel):
    """Configuration for storage service."""

    enabled: bool = Field(..., description="Whether object storage is enabled")
    endpoint: str = Field(..., description="Storage endpoint URL")
    access_key: str = Field(..., description="Access key for authentication")
    secret_key: str = Field(..., description="Secret key for authentication")
    bucket_name: str = Field(..., description="Bucket name for storing files")
    use_ssl: bool = Field(False, description="Whether to use SSL/TLS")
    legacy_base_path: Path = Field(
        default=Path("data/pdfs"),
        description="Base path for legacy local storage",
    )


class IStorageService(ABC):
    """Abstract interface for storage service."""

    @abstractmethod
    async def save_file(
        self,
        file_content: bytes,
        object_key: str,
        content_type: str = "application/pdf",
    ) -> str:
        """
        Save a file to storage.

        Args:
            file_content: File content as bytes.
            object_key: Object key (path) in storage.
            content_type: MIME type of the file.

        Returns:
            Storage path/key where file was saved.

        Raises:
            StorageError: If save operation fails.
        """
        pass

    @abstractmethod
    async def get_file(self, object_key: str) -> bytes:
        """
        Retrieve a file from storage.

        Args:
            object_key: Object key (path) in storage.

        Returns:
            File content as bytes.

        Raises:
            FileNotFoundError: If file doesn't exist.
            StorageError: If retrieval fails.
        """
        pass

    @abstractmethod
    async def delete_file(self, object_key: str) -> None:
        """
        Delete a file from storage.

        Args:
            object_key: Object key (path) in storage.

        Raises:
            FileNotFoundError: If file doesn't exist.
            StorageError: If deletion fails.
        """
        pass

    @abstractmethod
    async def file_exists(self, object_key: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            object_key: Object key (path) in storage.

        Returns:
            True if file exists, False otherwise.
        """
        pass

    @abstractmethod
    async def calculate_file_hash(self, object_key: str) -> str:
        """
        Calculate SHA256 hash of a file.

        Args:
            object_key: Object key (path) in storage.

        Returns:
            Hexadecimal hash string.

        Raises:
            FileNotFoundError: If file doesn't exist.
            StorageError: If calculation fails.
        """
        pass

    @abstractmethod
    def get_file_url(self, object_key: str) -> str:
        """
        Get accessible URL for a file.

        Args:
            object_key: Object key (path) in storage.

        Returns:
            URL string (may be a presigned URL or local path).
        """
        pass


class MinIOStorageService(IStorageService):
    """MinIO/S3-compatible object storage service."""

    def __init__(self, config: StorageServiceConfig):
        """Initialize MinIO storage service.

        Args:
            config: Storage service configuration.
        """
        self.config = config
        self._client: Minio | None = None
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        """Initialize MinIO client and ensure bucket exists."""
        if self._client is None:
            self._client = Minio(
                endpoint=self.config.endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=self.config.use_ssl,
            )

            # Ensure bucket exists
            try:
                if not self._client.bucket_exists(self.config.bucket_name):
                    logger.info(
                        f"Creating bucket '{self.config.bucket_name}' in MinIO",
                        extra={"bucket": self.config.bucket_name},
                    )
                    self._client.make_bucket(self.config.bucket_name)
            except S3Error as e:
                logger.error(
                    f"Failed to ensure bucket exists: {e}",
                    exc_info=True,
                    extra={"bucket": self.config.bucket_name},
                )
                raise

    async def save_file(
        self,
        file_content: bytes,
        object_key: str,
        content_type: str = "application/pdf",
    ) -> str:
        """Save a file to MinIO storage."""
        self._ensure_initialized()

        try:
            # Upload file to MinIO
            file_stream = io.BytesIO(file_content)
            self._client.put_object(
                bucket_name=self.config.bucket_name,
                object_name=object_key,
                data=file_stream,
                length=len(file_content),
                content_type=content_type,
            )

            logger.debug(
                f"Saved file to MinIO: {object_key}",
                extra={"object_key": object_key, "size": len(file_content)},
            )

            return object_key
        except S3Error as e:
            logger.error(
                f"Failed to save file to MinIO: {e}",
                exc_info=True,
                extra={"object_key": object_key},
            )
            raise RuntimeError(f"Failed to save file to MinIO: {e}") from e

    async def get_file(self, object_key: str) -> bytes:
        """Retrieve a file from MinIO storage."""
        self._ensure_initialized()

        try:
            response = self._client.get_object(
                bucket_name=self.config.bucket_name,
                object_name=object_key,
            )
            file_content = response.read()
            response.close()
            response.release_conn()

            logger.debug(
                f"Retrieved file from MinIO: {object_key}",
                extra={"object_key": object_key, "size": len(file_content)},
            )

            return file_content
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(f"File not found: {object_key}") from e
            logger.error(
                f"Failed to retrieve file from MinIO: {e}",
                exc_info=True,
                extra={"object_key": object_key},
            )
            raise RuntimeError(f"Failed to retrieve file from MinIO: {e}") from e

    async def delete_file(self, object_key: str) -> None:
        """Delete a file from MinIO storage."""
        self._ensure_initialized()

        try:
            self._client.remove_object(
                bucket_name=self.config.bucket_name,
                object_name=object_key,
            )

            logger.debug(
                f"Deleted file from MinIO: {object_key}",
                extra={"object_key": object_key},
            )
        except S3Error as e:
            logger.error(
                f"Failed to delete file from MinIO: {e}",
                exc_info=True,
                extra={"object_key": object_key},
            )
            raise RuntimeError(f"Failed to delete file from MinIO: {e}") from e

    async def file_exists(self, object_key: str) -> bool:
        """Check if a file exists in MinIO storage."""
        self._ensure_initialized()

        try:
            self._client.stat_object(
                bucket_name=self.config.bucket_name,
                object_name=object_key,
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error(
                f"Failed to check file existence in MinIO: {e}",
                exc_info=True,
                extra={"object_key": object_key},
            )
            raise RuntimeError(f"Failed to check file existence in MinIO: {e}") from e

    async def calculate_file_hash(self, object_key: str) -> str:
        """Calculate SHA256 hash of a file in MinIO storage."""
        file_content = await self.get_file(object_key)

        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_content)

        return sha256_hash.hexdigest()

    def get_file_url(self, object_key: str) -> str:
        """Get accessible URL for a file in MinIO storage."""
        protocol = "https" if self.config.use_ssl else "http"
        return f"{protocol}://{self.config.endpoint}/{self.config.bucket_name}/{object_key}"


class LegacyLocalStorageService(IStorageService):
    """Legacy local file system storage service."""

    def __init__(self, config: StorageServiceConfig):
        """Initialize local storage service.

        Args:
            config: Storage service configuration.
        """
        self.config = config
        self.base_path = config.legacy_base_path

    def _get_full_path(self, object_key: str) -> Path:
        """Convert object key to full file system path."""
        return self.base_path / object_key

    async def save_file(
        self,
        file_content: bytes,
        object_key: str,
        content_type: str = "application/pdf",
    ) -> str:
        """Save a file to local storage."""
        full_path = self._get_full_path(object_key)

        try:
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(full_path, "wb") as f:
                f.write(file_content)

            logger.debug(
                f"Saved file to local storage: {full_path}",
                extra={"object_key": object_key, "size": len(file_content)},
            )

            return str(full_path)
        except Exception as e:
            logger.error(
                f"Failed to save file to local storage: {e}",
                exc_info=True,
                extra={"object_key": object_key},
            )
            raise RuntimeError(f"Failed to save file to local storage: {e}") from e

    async def get_file(self, object_key: str) -> bytes:
        """Retrieve a file from local storage."""
        full_path = self._get_full_path(object_key)

        try:
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {full_path}")

            with open(full_path, "rb") as f:
                file_content = f.read()

            logger.debug(
                f"Retrieved file from local storage: {full_path}",
                extra={"object_key": object_key, "size": len(file_content)},
            )

            return file_content
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to retrieve file from local storage: {e}",
                exc_info=True,
                extra={"object_key": object_key},
            )
            raise RuntimeError(f"Failed to retrieve file from local storage: {e}") from e

    async def delete_file(self, object_key: str) -> None:
        """Delete a file from local storage."""
        full_path = self._get_full_path(object_key)

        try:
            if full_path.exists():
                full_path.unlink()
                logger.debug(
                    f"Deleted file from local storage: {full_path}",
                    extra={"object_key": object_key},
                )
        except Exception as e:
            logger.error(
                f"Failed to delete file from local storage: {e}",
                exc_info=True,
                extra={"object_key": object_key},
            )
            raise RuntimeError(f"Failed to delete file from local storage: {e}") from e

    async def file_exists(self, object_key: str) -> bool:
        """Check if a file exists in local storage."""
        full_path = self._get_full_path(object_key)
        return full_path.exists()

    async def calculate_file_hash(self, object_key: str) -> str:
        """Calculate SHA256 hash of a file in local storage."""
        file_content = await self.get_file(object_key)

        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_content)

        return sha256_hash.hexdigest()

    def get_file_url(self, object_key: str) -> str:
        """Get accessible path for a file in local storage."""
        full_path = self._get_full_path(object_key)
        return str(full_path)


class StorageService(IStorageService):
    """Unified storage service with automatic fallback."""

    def __init__(self, config: StorageServiceConfig):
        """Initialize storage service.

        Uses MinIO if enabled, otherwise falls back to local storage.

        Args:
            config: Storage service configuration.
        """
        self.config = config
        if config.enabled:
            self._primary_storage = MinIOStorageService(config)
        else:
            self._primary_storage = LegacyLocalStorageService(config)

        logger.info(
            f"Storage service initialized: {'MinIO' if config.enabled else 'Local'}",
            extra={
                "enabled": config.enabled,
                "endpoint": config.endpoint if config.enabled else None,
                "bucket": config.bucket_name if config.enabled else None,
            },
        )

    async def save_file(
        self,
        file_content: bytes,
        object_key: str,
        content_type: str = "application/pdf",
    ) -> str:
        """Save a file to storage."""
        return await self._primary_storage.save_file(file_content, object_key, content_type)

    async def get_file(self, object_key: str) -> bytes:
        """Retrieve a file from storage."""
        return await self._primary_storage.get_file(object_key)

    async def delete_file(self, object_key: str) -> None:
        """Delete a file from storage."""
        await self._primary_storage.delete_file(object_key)

    async def file_exists(self, object_key: str) -> bool:
        """Check if a file exists in storage."""
        return await self._primary_storage.file_exists(object_key)

    async def calculate_file_hash(self, object_key: str) -> str:
        """Calculate SHA256 hash of a file."""
        return await self._primary_storage.calculate_file_hash(object_key)

    def get_file_url(self, object_key: str) -> str:
        """Get accessible URL for a file."""
        return self._primary_storage.get_file_url(object_key)


def create_storage_service(config: StorageServiceConfig) -> IStorageService:
    """
    Create a storage service instance based on configuration.

    Args:
        config: Storage service configuration.

    Returns:
        Storage service instance.
    """
    return StorageService(config)
