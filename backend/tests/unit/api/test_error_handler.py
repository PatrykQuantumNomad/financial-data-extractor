"""
Unit tests for ErrorHandler middleware.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from app.api.middleware.fastapi_error_handler import (ErrorHandler,
                                                      ProblemDetails)
from app.core.exceptions.custom_exceptions import (BusinessLogicError, Error,
                                                   ErrorType, ForbiddenError,
                                                   JSONFileNotFoundError,
                                                   JSONInvalidEncodingError,
                                                   JSONInvalidError)
from fastapi import FastAPI, HTTPException, Request, status


@pytest.mark.unit
class TestErrorHandler:
    """Test cases for ErrorHandler middleware."""

    @pytest.fixture
    def mock_app(self) -> MagicMock:
        """Create a mock FastAPI app."""
        app = MagicMock(spec=FastAPI)
        app.add_exception_handler = Mock()
        return app

    @pytest.fixture
    def mock_logger(self) -> logging.Logger:
        """Create a mock logger."""
        return logging.getLogger("test")

    @pytest.fixture
    def error_handler(self, mock_app, mock_logger) -> ErrorHandler:
        """Create an ErrorHandler instance."""
        return ErrorHandler(app=mock_app, logger=mock_logger)

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock Request."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-request-id"
        request.url = MagicMock()
        request.url.path = "/test/path"
        request.method = "GET"
        return request

    def test_register_default_handlers(self, error_handler: ErrorHandler):
        """Test registering default exception handlers."""
        # Arrange
        expected_handlers = 8

        # Act
        error_handler.register_default_handlers()

        # Assert
        assert error_handler.app.add_exception_handler.call_count == expected_handlers

    @pytest.mark.asyncio
    async def test_forbidden_error_handler_returns_403(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test ForbiddenError handler returns 403."""
        # Arrange
        exc = ForbiddenError(detail="Access denied")
        expected_type = ErrorType.FORBIDDEN.value
        expected_status = status.HTTP_403_FORBIDDEN

        # Act
        response = await error_handler.forbidden_error_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status
        assert response.media_type == "application/problem+json"

        # Parse response body
        import json
        body = json.loads(response.body.decode())
        assert body["type"] == expected_type
        assert body["status"] == expected_status
        assert "Access denied" in body["detail"]
        assert "[Request ID: test-request-id]" in body["detail"]

    @pytest.mark.asyncio
    async def test_business_logic_error_handler_returns_400(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test BusinessLogicError handler returns 400."""
        # Arrange
        exc = BusinessLogicError(detail="Invalid business logic")
        expected_status = status.HTTP_400_BAD_REQUEST

        # Act
        response = await error_handler.business_logic_error_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_json_file_not_found_error_handler_returns_404(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test JSONFileNotFoundError handler returns 404."""
        # Arrange
        exc = JSONFileNotFoundError(filename="test.json")
        expected_status = status.HTTP_404_NOT_FOUND

        # Act
        response = await error_handler.json_file_not_found_error_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_json_invalid_error_handler_returns_400(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test JSONInvalidError handler returns 400."""
        # Arrange
        exc = JSONInvalidError(filename="test.json", error="Invalid JSON")
        expected_status = status.HTTP_400_BAD_REQUEST

        # Act
        response = await error_handler.json_invalid_error_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_json_invalid_encoding_error_handler_returns_415(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test JSONInvalidEncodingError handler returns 415."""
        # Arrange
        exc = JSONInvalidEncodingError(filename="test.json", error="Invalid encoding")
        expected_status = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

        # Act
        response = await error_handler.json_invalid_encoding_error_handler(
            mock_request, exc
        )

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_custom_error_handler_returns_appropriate_status(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test generic custom Error handler returns appropriate status."""
        # Arrange
        exc = Error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Generic error",
            title="Error",
        )
        expected_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        # Act
        response = await error_handler.custom_error_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_http_exception_handler_returns_status_code(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test HTTPException handler returns appropriate status code."""
        # Arrange
        exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        expected_status = status.HTTP_404_NOT_FOUND

        # Act
        response = await error_handler.http_exception_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_general_exception_handler_returns_500(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test general exception handler returns 500."""
        # Arrange
        exc = ValueError("Unexpected error")
        expected_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        # Act
        response = await error_handler.general_exception_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_create_problem_response_with_request_id(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test that request ID is included in response when available."""
        # Arrange
        exc = ForbiddenError(detail="Access denied")

        # Act
        response = await error_handler._create_problem_response(
            request=mock_request,
            exc=exc,
            status_code=status.HTTP_403_FORBIDDEN,
            type_=ErrorType.FORBIDDEN.value,
            title="Forbidden",
            detail="Access denied",
        )

        # Assert
        import json
        body = json.loads(response.body.decode())
        assert "[Request ID: test-request-id]" in body["detail"]

    @pytest.mark.asyncio
    async def test_create_problem_response_without_request_id(
        self, error_handler: ErrorHandler
    ):
        """Test that response works without request ID."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        mock_request.state.request_id = None  # No request ID
        mock_request.url = MagicMock()
        exc = ForbiddenError(detail="Access denied")

        # Act
        response = await error_handler._create_problem_response(
            request=mock_request,
            exc=exc,
            status_code=status.HTTP_403_FORBIDDEN,
            type_=ErrorType.FORBIDDEN.value,
            title="Forbidden",
            detail="Access denied",
        )

        # Assert
        import json
        body = json.loads(response.body.decode())
        assert "[Request ID:" not in body["detail"]

    @pytest.mark.asyncio
    async def test_create_problem_response_uses_exc_detail_when_detail_is_none(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test that exc.detail is used when detail is None."""
        # Arrange
        exc = MagicMock()
        exc.detail = "Exception detail"

        # Act
        response = await error_handler._create_problem_response(
            request=mock_request,
            exc=exc,
            status_code=status.HTTP_400_BAD_REQUEST,
            type_="test-type",
            title="Test Title",
            detail=None,
        )

        # Assert
        import json
        body = json.loads(response.body.decode())
        # Request ID is prepended to detail when available
        assert "Exception detail" in body["detail"]
        assert "[Request ID:" in body["detail"]

    @pytest.mark.asyncio
    async def test_response_includes_instance_url(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test that response includes instance URL."""
        # Arrange
        mock_request.url = Mock()
        mock_request.url.__str__ = Mock(return_value="https://example.com/test/path")
        exc = ForbiddenError(detail="Access denied")

        # Act
        response = await error_handler._create_problem_response(
            request=mock_request,
            exc=exc,
            status_code=status.HTTP_403_FORBIDDEN,
            type_=ErrorType.FORBIDDEN.value,
            title="Forbidden",
            detail="Access denied",
        )

        # Assert
        import json
        body = json.loads(response.body.decode())
        assert body["instance"] == "https://example.com/test/path"
