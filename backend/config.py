"""
This module provides a Pydantic-based settings configuration.

It reads the configuration values from environment variables,
with a fallback to a `.env` file.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centralized configuration settings for the FastAPI application.
    """

    # PostgreSQL configuration
    db_host: str = Field(..., description="Hostname or IP address of the PostgreSQL server.")
    db_port: int = Field(
        5432, description="Port number on which the PostgreSQL server is listening."
    )
    db_name: str = Field(..., description="Name of the PostgreSQL database.")
    db_username: str = Field(..., description="Username for authenticating with PostgreSQL.")
    db_password: str = Field(..., description="Password for authenticating with PostgreSQL.")

    @computed_field
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL from individual components."""
        return (
            f"postgresql://{quote_plus(self.db_username)}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # Redis configuration
    redis_host: str = Field(..., description="Hostname or IP address of the Redis server.")
    redis_port: int = Field(6379, description="Port number on which the Redis server is listening.")
    redis_db: int = Field(0, description="Database number for Redis.")
    redis_password: str = Field(..., description="Password for authenticating with Redis.")
    redis_max_connections: int = Field(10, description="Maximum number of connections to Redis.")

    # LLM configuration
    openai_api_key: str = Field(..., description="API key for OpenAI services.")
    open_router_api_key: str = Field(..., description="API key for OpenRouter services.")

    # PDF storage configuration (legacy local storage)
    pdf_storage_base_path: str = Field(
        "data/pdfs", description="Base path for storing PDF documents (legacy)."
    )
    max_crawl_depth: int = Field(
        2, description="Maximum depth for deep crawling investor relations websites."
    )

    # MinIO (S3-compatible) object storage configuration
    minio_enabled: bool = Field(
        True, description="Whether to use MinIO/S3 object storage for PDF files."
    )
    minio_endpoint: str = Field(
        ..., description="MinIO/S3 endpoint URL (e.g., localhost:9000)."
    )
    minio_access_key: str = Field(
        ..., description="MinIO/S3 access key."
    )
    minio_secret_key: str = Field(
        ..., description="MinIO/S3 secret key."
    )
    minio_bucket_name: str = Field(
        "financial-documents", description="Bucket name for storing PDF files."
    )
    minio_use_ssl: bool = Field(
        False, description="Whether to use SSL/TLS for MinIO connection."
    )

    # Server configuration
    host: str = Field("0.0.0.0", description="Host address where the server will listen.")
    port: int = Field(3030, description="Port number on which the server will run.")
    request_timeout: int = Field(
        60, description="Timeout duration for incoming requests in seconds."
    )
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="List of origins that are allowed to make cross-origin requests.",
    )
    server_log_level: str = Field("info", description="Log level for server-related logs.")
    app_log_level: str = Field("debug", description="Log level for application-specific logs.")
    logging_path: str = Field("logging.json", description="Path to the logging configuration file.")
    app_name: str = Field(
        "financial-data-extractor-api", description="Name of the FastAPI application."
    )
    app_version: str = Field("1.0.0", description="Version of the FastAPI application.")

    model_config = {"env_file": ".env", "frozen": True}


def get_settings() -> Settings:
    """Get application settings instance.

    Returns:
        Settings instance loaded from environment variables.
    """
    return Settings()
