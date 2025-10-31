"""
Company model for storing company information.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.document import Document
    from app.db.models.extraction import CompiledStatement


class Company(Base):
    """Company model representing a tracked company."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ticker: Mapped[str] = mapped_column(String(length=10), nullable=False, unique=True, index=True)
    ir_url: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    compiled_statements: Mapped[list["CompiledStatement"]] = relationship(
        "CompiledStatement", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Company."""
        return f"<Company(id={self.id}, name='{self.name}', ticker='{self.ticker}')>"
