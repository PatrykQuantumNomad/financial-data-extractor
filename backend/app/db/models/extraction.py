"""
Extraction and CompiledStatement models for storing LLM extractions.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.document import Document


class Extraction(Base):
    """Extraction model for storing raw LLM extraction data."""

    __tablename__ = "extractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statement_type: Mapped[str] = mapped_column(String(length=50), nullable=False, index=True)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="extractions")

    def __repr__(self) -> str:
        """String representation of Extraction."""
        return f"<Extraction(id={self.id}, document_id={self.document_id}, statement_type='{self.statement_type}')>"


class CompiledStatement(Base):
    """CompiledStatement model for storing compiled multi-year financial statements."""

    __tablename__ = "compiled_statements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statement_type: Mapped[str] = mapped_column(String(length=50), nullable=False, index=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True, onupdate=func.now()
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="compiled_statements")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("company_id", "statement_type", name="uq_company_statement_type"),
    )

    def __repr__(self) -> str:
        """String representation of CompiledStatement."""
        return f"<CompiledStatement(id={self.id}, company_id={self.company_id}, statement_type='{self.statement_type}')>"
