"""
Document model for storing PDF documents and annual reports.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.extraction import Extraction


class Document(Base):
    """Document model representing a PDF document or annual report."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(length=50), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="documents")
    extractions: Mapped[list["Extraction"]] = relationship(
        "Extraction", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Document."""
        return f"<Document(id={self.id}, company_id={self.company_id}, fiscal_year={self.fiscal_year}, type='{self.document_type}')>"
