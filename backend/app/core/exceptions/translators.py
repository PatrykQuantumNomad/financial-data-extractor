"""
Exception translation utilities.

These functions translate exceptions between layers:
- DB exceptions -> Service exceptions
- Service exceptions -> API exceptions

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import NoReturn

from sqlalchemy.exc import IntegrityError, OperationalError

from app.core.exceptions.api_exceptions import BadRequestError, InternalServerError, NotFoundError
from app.core.exceptions.db_exceptions import (
    BaseDatabaseError,
    DatabaseConnectionError,
    DatabaseIntegrityError,
    DatabaseTransactionError,
)
from app.core.exceptions.db_exceptions import EntityNotFoundError as DbEntityNotFoundError
from app.core.exceptions.service_exceptions import (
    BaseServiceError,
    BusinessLogicError,
    ServiceUnavailableError,
    ValidationError,
)
from app.core.exceptions.service_exceptions import EntityNotFoundError as ServiceEntityNotFoundError

logger = logging.getLogger(__name__)


def translate_db_exception_to_service(
    db_exception: Exception,
) -> BaseServiceError:
    """
    Translate a database layer exception to a service layer exception.

    Args:
        db_exception: The database exception to translate.

    Returns:
        A service layer exception.

    Raises:
        BaseServiceException: Always raises a translated service exception.
    """
    # Handle known database exceptions
    if isinstance(db_exception, DbEntityNotFoundError):
        return ServiceEntityNotFoundError(
            entity_name=db_exception.entity_name,
            entity_id=db_exception.entity_id,
        )

    if isinstance(db_exception, DatabaseIntegrityError):
        return ValidationError(
            message=f"Data integrity violation: {db_exception.message}",
            entity_name=db_exception.entity_name,
        )

    if isinstance(db_exception, DatabaseConnectionError):
        return ServiceUnavailableError(
            message=f"Database unavailable: {db_exception.message}",
            service_name="database",
        )

    if isinstance(db_exception, DatabaseTransactionError):
        return ServiceUnavailableError(
            message=f"Transaction failed: {db_exception.message}",
            service_name="database",
        )

    if isinstance(db_exception, BaseDatabaseError):
        return ServiceUnavailableError(
            message=f"Database error: {db_exception.message}",
            service_name="database",
        )

    # Handle SQLAlchemy exceptions
    if isinstance(db_exception, IntegrityError):
        # Extract constraint name if available
        constraint_name = None
        if hasattr(db_exception.orig, "diag") and hasattr(db_exception.orig.diag, "constraint_name"):
            constraint_name = db_exception.orig.diag.constraint_name
        elif hasattr(db_exception.orig, "pgcode"):
            # PostgreSQL specific (fallback)
            constraint_name = str(db_exception.orig)
        constraint_info = f" (constraint: {constraint_name})" if constraint_name else ""
        return ValidationError(
            message=f"Data integrity violation{constraint_info}: {str(db_exception.orig)}",
            entity_name=None,
        )

    if isinstance(db_exception, OperationalError):
        return ServiceUnavailableError(
            message=f"Database operation failed: {str(db_exception)}",
            service_name="database",
        )

    # Fallback for unknown database exceptions
    logger.error(
        f"Unknown database exception type: {type(db_exception)}, " f"message: {str(db_exception)}"
    )
    return ServiceUnavailableError(
        message=f"Unexpected database error: {str(db_exception)}",
        service_name="database",
    )


def translate_service_exception_to_api(
    service_exception: Exception,
) -> NoReturn:
    """
    Translate a service layer exception to an API layer exception.

    Args:
        service_exception: The service exception to translate.

    Returns:
        Never returns, always raises an API exception.

    Raises:
        ApiError: Always raises a translated API exception.
    """
    # Handle known service exceptions
    if isinstance(service_exception, ServiceEntityNotFoundError):
        detail = service_exception.message
        raise NotFoundError(detail=detail)

    if isinstance(service_exception, ValidationError):
        detail = service_exception.message
        raise BadRequestError(detail=detail)

    if isinstance(service_exception, BusinessLogicError):
        detail = service_exception.message
        raise BadRequestError(detail=detail)

    if isinstance(service_exception, ServiceUnavailableError):
        detail = f"Service unavailable: {service_exception.message}"
        raise InternalServerError(detail=detail)

    if isinstance(service_exception, BaseServiceError):
        detail = service_exception.message
        raise InternalServerError(detail=detail)

    # Fallback for unknown service exceptions
    logger.error(
        f"Unknown service exception type: {type(service_exception)}, "
        f"message: {str(service_exception)}"
    )
    raise InternalServerError(detail=f"Unexpected service error: {str(service_exception)}")
