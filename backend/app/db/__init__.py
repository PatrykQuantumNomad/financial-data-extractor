"""
Database module for the financial data extractor.

This module provides database connections, models, and utilities for interacting
with the PostgreSQL database.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from app.db.base import Base, SessionLocal, engine

__all__ = ["Base", "SessionLocal", "engine"]
