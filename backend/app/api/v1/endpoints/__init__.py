"""
REST API endpoints for financial data extractor.

This module exports all endpoint routers for the API v1.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from app.api.v1.endpoints.companies import router as companies_router
from app.api.v1.endpoints.compiled_statements import router as compiled_statements_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.extractions import router as extractions_router

__all__ = [
    "companies_router",
    "documents_router",
    "extractions_router",
    "compiled_statements_router",
]
