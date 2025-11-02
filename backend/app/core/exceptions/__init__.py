"""
Exception classes organized by layer.

This module provides exceptions for different layers:
- db_exceptions: Database/repository layer exceptions
- service_exceptions: Service/business logic layer exceptions
- api_exceptions: API/endpoint layer exceptions
- translators: Functions to translate exceptions between layers

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

# Backward compatibility: Export the old Error class as ApiError
# Keep BusinessLogicError for backward compatibility
# API layer exceptions
from app.core.exceptions.api_exceptions import (
                                                ApiError,
                                                BadRequestError,
                                                ErrorType,
                                                ForbiddenError,
                                                InternalServerError,
                                                JSONFileError,
                                                JSONFileNotFoundError,
                                                JSONInvalidEncodingError,
                                                JSONInvalidError,
                                                NotFoundError,
)
from app.core.exceptions.api_exceptions import ApiError as Error

# Database layer exceptions
from app.core.exceptions.db_exceptions import (
                                                BaseDatabaseError,
                                                DatabaseConnectionError,
                                                DatabaseIntegrityError,
                                                DatabaseTransactionError,
)
from app.core.exceptions.db_exceptions import EntityNotFoundError as DbEntityNotFoundError

# Service layer exceptions
from app.core.exceptions.service_exceptions import (
                                                BaseServiceError,
                                                BusinessLogicError,
                                                ServiceUnavailableError,
                                                ValidationError,
)
from app.core.exceptions.service_exceptions import EntityNotFoundError as ServiceEntityNotFoundError

# Translation utilities
from app.core.exceptions.translators import (
                                                translate_db_exception_to_service,
                                                translate_service_exception_to_api,
)

__all__ = [
    # Database exceptions
    "BaseDatabaseError",
    "DatabaseConnectionError",
    "DatabaseIntegrityError",
    "DatabaseTransactionError",
    "DbEntityNotFoundError",
    # Service exceptions
    "BaseServiceError",
    "ServiceEntityNotFoundError",
    "ValidationError",
    "BusinessLogicError",
    "ServiceUnavailableError",
    # API exceptions
    "ApiError",
    "Error",  # Backward compatibility
    "BadRequestError",
    "NotFoundError",
    "ForbiddenError",
    "InternalServerError",
    "ErrorType",
    "JSONFileError",
    "JSONFileNotFoundError",
    "JSONInvalidError",
    "JSONInvalidEncodingError",
    # Translators
    "translate_db_exception_to_service",
    "translate_service_exception_to_api",
]
