"""
REST API endpoints for Company resource.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import JSONResponse

from app.core.exceptions.service_exceptions import BaseServiceError
from app.core.exceptions.translators import translate_service_exception_to_api
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.company import CompanyService
from app.services.dependencies import get_company_service

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company",
    description="Create a new company with the provided information.",
)
async def create_company(
    company_data: CompanyCreate,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    """Create a new company.

    Args:
        company_data: Company creation data.
        company_service: Company service (injected).

    Returns:
        Created company data.

    Raises:
        BadRequestError: If validation fails.
        InternalServerError: If service operation fails.
    """
    try:
        company = await company_service.create_company(company_data)
        return CompanyResponse.model_validate(company)
    except BaseServiceError as e:
        translate_service_exception_to_api(e)


@router.get(
    "",
    response_model=list[CompanyResponse],
    summary="List all companies",
    description="Get a paginated list of all companies.",
)
async def list_companies(
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of records to return")
    ] = 100,
) -> list[CompanyResponse]:
    """List all companies with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        company_service: Company service (injected).

    Returns:
        List of companies.
    """
    companies = await company_service.get_all_companies(skip=skip, limit=limit)
    return [CompanyResponse.model_validate(company) for company in companies]


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get company by ID",
    description="Get a specific company by its ID.",
)
async def get_company(
    company_id: Annotated[int, Path(description="Company ID")],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    """Get a company by ID.

    Args:
        company_id: Company ID.
        company_service: Company service (injected).

    Returns:
        Company data.

    Raises:
        NotFoundError: If company not found.
        InternalServerError: If service operation fails.
    """
    try:
        company = await company_service.get_company(company_id)
        return CompanyResponse.model_validate(company)
    except BaseServiceError as e:
        translate_service_exception_to_api(e)


@router.get(
    "/ticker/{ticker}",
    response_model=CompanyResponse,
    summary="Get company by ticker",
    description="Get a company by its ticker symbol.",
)
async def get_company_by_ticker(
    ticker: Annotated[str, Path(description="Stock ticker symbol")],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    """Get a company by ticker symbol.

    Args:
        ticker: Stock ticker symbol.
        company_service: Company service (injected).

    Returns:
        Company data.

    Raises:
        NotFoundError: If company not found.
        InternalServerError: If service operation fails.
    """
    try:
        company = await company_service.get_company_by_ticker(ticker)
        return CompanyResponse.model_validate(company)
    except BaseServiceError as e:
        translate_service_exception_to_api(e)


@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update a company",
    description="Update an existing company with the provided information.",
)
async def update_company(
    company_id: Annotated[int, Path(description="Company ID")],
    company_data: CompanyUpdate,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    """Update a company.

    Args:
        company_id: Company ID.
        company_data: Company update data.
        company_service: Company service (injected).

    Returns:
        Updated company data.

    Raises:
        NotFoundError: If company not found.
        BadRequestError: If validation fails.
        InternalServerError: If service operation fails.
    """
    try:
        company = await company_service.update_company(company_id, company_data)
        return CompanyResponse.model_validate(company)
    except BaseServiceError as e:
        translate_service_exception_to_api(e)


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a company",
    description="Delete a company by its ID.",
)
async def delete_company(
    company_id: Annotated[int, Path(description="Company ID")],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> JSONResponse:
    """Delete a company.

    Args:
        company_id: Company ID.
        company_service: Company service (injected).

    Returns:
        Empty response with 204 status code.

    Raises:
        NotFoundError: If company not found.
        InternalServerError: If deletion fails.
    """
    try:
        await company_service.delete_company(company_id)
        return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
    except BaseServiceError as e:
        translate_service_exception_to_api(e)
