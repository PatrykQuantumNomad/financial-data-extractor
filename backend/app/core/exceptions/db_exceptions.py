"""
Database layer exception classes.

These exceptions are used exclusively in the database/repository layer.
They should not be raised directly in service or API layers.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""


class BaseDatabaseError(Exception):
    """Base exception for all database layer errors."""

    def __init__(self, message: str, entity_name: str | None = None) -> None:
        """
        Initialize base database exception.

        Args:
            message: Error message.
            entity_name: Name of the entity involved (e.g., 'Company', 'Document').
        """
        self.message = message
        self.entity_name = entity_name
        super().__init__(self.message)


class EntityNotFoundError(BaseDatabaseError):
    """Raised when an entity is not found in the database."""

    def __init__(self, entity_name: str, entity_id: int | str | None = None) -> None:
        """
        Initialize entity not found error.

        Args:
            entity_name: Name of the entity (e.g., 'Company', 'Document').
            entity_id: ID of the entity that was not found.
        """
        if entity_id is not None:
            message = f"{entity_name} with id {entity_id} not found in database"
        else:
            message = f"{entity_name} not found in database"
        super().__init__(message=message, entity_name=entity_name)
        self.entity_id = entity_id


class DatabaseIntegrityError(BaseDatabaseError):
    """Raised when a database integrity constraint is violated."""

    def __init__(
        self,
        message: str,
        constraint_name: str | None = None,
        entity_name: str | None = None,
    ) -> None:
        """
        Initialize database integrity error.

        Args:
            message: Error message.
            constraint_name: Name of the violated constraint.
            entity_name: Name of the entity involved.
        """
        super().__init__(message=message, entity_name=entity_name)
        self.constraint_name = constraint_name


class DatabaseConnectionError(BaseDatabaseError):
    """Raised when there's a database connection issue."""

    def __init__(self, message: str = "Database connection failed") -> None:
        """
        Initialize database connection error.

        Args:
            message: Error message.
        """
        super().__init__(message=message)


class DatabaseTransactionError(BaseDatabaseError):
    """Raised when a database transaction fails."""

    def __init__(self, message: str = "Database transaction failed") -> None:
        """
        Initialize database transaction error.

        Args:
            message: Error message.
        """
        super().__init__(message=message)
