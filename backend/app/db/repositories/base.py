"""
Base repository class providing common database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    """Base repository providing common database operations using async SQLAlchemy sessions."""

    def __init__(self, session: AsyncSession | None = None):
        """Initialize repository with database session.

        Args:
            session: Optional async session. If None, creates a new session.
        """
        self._session = session
        self._session_owned = session is None

    @property
    def session(self) -> AsyncSession:
        """Get or create async session."""
        if self._session is None:
            self._session = AsyncSessionLocal()
        return self._session

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._session_owned and self._session is not None:
            await self._session.close()
            self._session = None

    def _model_to_schema(self, model: Any, schema_class: type[T]) -> T:
        """Convert SQLAlchemy model to Pydantic schema.

        Args:
            model: SQLAlchemy model instance.
            schema_class: Pydantic schema class with from_attributes=True.

        Returns:
            Pydantic schema instance.

        Raises:
            ValueError: If model is None.
        """
        if model is None:
            raise ValueError("Cannot convert None to schema")
        return schema_class.model_validate(model)

    async def _handle_db_operation(self, operation_name: str) -> None:
        """Handle database operations and translate SQLAlchemy exceptions.

        This is a context manager helper that can be used to wrap database operations.
        For now, we'll rely on individual methods to catch and translate exceptions.

        Args:
            operation_name: Name of the operation being performed.

        Raises:
            DatabaseIntegrityError: If integrity constraint is violated.
            DatabaseConnectionError: If connection fails.
            DatabaseTransactionError: If transaction fails.
        """
        # This method is a placeholder for future use if we want to
        # add automatic exception translation at the base level
        pass

    async def _model_to_dict(self, model: Any) -> dict[str, Any]:
        """Convert SQLAlchemy model to dictionary.

        Args:
            model: SQLAlchemy model instance.

        Returns:
            Dictionary representation of the model.
        """
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            # Handle datetime serialization
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            result[column.name] = value
        return result
