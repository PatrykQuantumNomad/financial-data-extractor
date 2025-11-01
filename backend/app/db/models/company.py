"""
Company model for storing company information.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from typing import TYPE_CHECKING

from app.db.base import Base
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.db.models.document import Document
    from app.db.models.extraction import CompiledStatement


class Company(Base):
    """Company model representing a tracked company."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    primary_ticker: Mapped[str | None] = mapped_column(String(length=10), nullable=True, index=True)
    tickers: Mapped[list[dict[str, str]] | None] = mapped_column(
        JSONB(astext_type=Text()), nullable=True
    )
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
        return f"<Company(id={self.id}, name='{self.name}', primary_ticker='{self.primary_ticker}')>"
