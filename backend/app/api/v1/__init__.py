"""
API v1 module for financial data extractor.

This module provides the main API router for v1 endpoints.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    companies_router,
    compiled_statements_router,
    documents_router,
    extractions_router,
    tasks_router,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(companies_router, prefix="/api/v1")
api_router.include_router(documents_router, prefix="/api/v1")
api_router.include_router(extractions_router, prefix="/api/v1")
api_router.include_router(compiled_statements_router, prefix="/api/v1")
api_router.include_router(tasks_router, prefix="/api/v1")

__all__ = ["api_router"]
