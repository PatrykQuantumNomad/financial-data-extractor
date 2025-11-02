"""
Service layer exception classes.

These exceptions are used exclusively in the service layer.
They represent business logic errors and should be translated
to API layer exceptions when crossing boundaries.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""


class BaseServiceError(Exception):
    """Base exception for all service layer errors."""

    def __init__(self, message: str, entity_name: str | None = None) -> None:
        """
        Initialize base service exception.

        Args:
            message: Error message.
            entity_name: Name of the entity involved (e.g., 'Company', 'Document').
        """
        self.message = message
        self.entity_name = entity_name
        super().__init__(self.message)


class EntityNotFoundError(BaseServiceError):
    """Raised when an entity is not found (business context)."""

    def __init__(self, entity_name: str, entity_id: int | str | None = None) -> None:
        """
        Initialize entity not found error.

        Args:
            entity_name: Name of the entity (e.g., 'Company', 'Document').
            entity_id: ID of the entity that was not found.
        """
        if entity_id is not None:
            message = f"{entity_name} with id {entity_id} not found"
        else:
            message = f"{entity_name} not found"
        super().__init__(message=message, entity_name=entity_name)
        self.entity_id = entity_id


class ValidationError(BaseServiceError):
    """Raised when business validation fails."""

    def __init__(
        self, message: str, field_name: str | None = None, entity_name: str | None = None
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Validation error message.
            field_name: Name of the field that failed validation.
            entity_name: Name of the entity involved.
        """
        super().__init__(message=message, entity_name=entity_name)
        self.field_name = field_name


class BusinessLogicError(BaseServiceError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str, entity_name: str | None = None) -> None:
        """
        Initialize business logic error.

        Args:
            message: Error message describing the business rule violation.
            entity_name: Name of the entity involved.
        """
        super().__init__(message=message, entity_name=entity_name)


class ServiceUnavailableError(BaseServiceError):
    """Raised when a service operation cannot be completed."""

    def __init__(self, message: str, service_name: str | None = None) -> None:
        """
        Initialize service unavailable error.

        Args:
            message: Error message.
            service_name: Name of the service that is unavailable.
        """
        super().__init__(message=message)
        self.service_name = service_name
