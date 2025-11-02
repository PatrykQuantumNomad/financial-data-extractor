"""
Unit tests for RequestIDMiddleware and TimeoutMiddleware.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.middleware.request_context import RequestIDMiddleware, TimeoutMiddleware


@pytest.mark.unit
class TestRequestIDMiddleware:
    """Test cases for RequestIDMiddleware."""

    @pytest.fixture
    def mock_app(self) -> MagicMock:
        """Create a mock ASGI app."""
        return MagicMock()

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock Request."""
        request = MagicMock()
        request.state = MagicMock()
        return request

    @pytest.fixture
    def mock_call_next(self) -> AsyncMock:
        """Create a mock call_next function."""
        response = MagicMock()
        response.headers = {}
        return AsyncMock(return_value=response)

    @pytest.fixture
    def middleware(self, mock_app) -> RequestIDMiddleware:
        """Create a RequestIDMiddleware instance."""
        return RequestIDMiddleware(mock_app)

    @pytest.mark.asyncio
    async def test_generates_unique_request_id(
        self, middleware: RequestIDMiddleware, mock_request: MagicMock, mock_call_next: AsyncMock
    ):
        """Test that unique request ID is generated."""
        # Arrange - already set up

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert hasattr(mock_request.state, "request_id")
        assert isinstance(mock_request.state.request_id, str)
        assert len(mock_request.state.request_id) > 0

    @pytest.mark.asyncio
    async def test_request_id_is_valid_uuid(
        self, middleware: RequestIDMiddleware, mock_request: MagicMock, mock_call_next: AsyncMock
    ):
        """Test that request ID is a valid UUID."""
        # Arrange - already set up

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        request_id = mock_request.state.request_id
        uuid.UUID(request_id)  # Should not raise ValueError

    @pytest.mark.asyncio
    async def test_request_id_added_to_response_header(
        self, middleware: RequestIDMiddleware, mock_request: MagicMock, mock_call_next: AsyncMock
    ):
        """Test that request ID is added to response header."""
        # Arrange - already set up

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == mock_request.state.request_id

    @pytest.mark.asyncio
    async def test_calls_next_middleware(
        self, middleware: RequestIDMiddleware, mock_request: MagicMock, mock_call_next: AsyncMock
    ):
        """Test that next middleware is called."""
        # Arrange - already set up

        # Act
        await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_called_once_with(mock_request)


@pytest.mark.unit
class TestTimeoutMiddleware:
    """Test cases for TimeoutMiddleware."""

    @pytest.fixture
    def mock_app(self) -> MagicMock:
        """Create a mock ASGI app."""
        return MagicMock()

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock Request."""
        return MagicMock()

    @pytest.fixture
    def timeout_value(self) -> int:
        """Timeout value in seconds."""
        return 1

    @pytest.fixture
    def middleware(self, mock_app, timeout_value: int) -> TimeoutMiddleware:
        """Create a TimeoutMiddleware instance."""
        return TimeoutMiddleware(mock_app, timeout=timeout_value)

    @pytest.mark.asyncio
    async def test_returns_response_when_request_completes_in_time(
        self, middleware: TimeoutMiddleware, mock_request: MagicMock
    ):
        """Test that response is returned when request completes within timeout."""
        # Arrange
        mock_response = MagicMock()
        async def mock_call_next(request):
            return mock_response

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_returns_504_when_request_times_out(
        self, middleware: TimeoutMiddleware, mock_request: MagicMock
    ):
        """Test that 504 is returned when request times out."""
        # Arrange
        async def slow_call_next(request):
            await asyncio.sleep(2)  # Exceed 1 second timeout
            return MagicMock()

        # Act
        response = await middleware.dispatch(mock_request, slow_call_next)

        # Assert
        assert response.status_code == 504

    @pytest.mark.asyncio
    async def test_timeout_error_response_has_detail_message(
        self, middleware: TimeoutMiddleware, mock_request: MagicMock
    ):
        """Test that timeout response has detail message."""
        # Arrange
        async def slow_call_next(request):
            await asyncio.sleep(2)  # Exceed 1 second timeout
            return MagicMock()

        # Act
        response = await middleware.dispatch(mock_request, slow_call_next)

        # Assert
        import json
        body = json.loads(response.body.decode())
        assert "detail" in body
        assert "timed out" in body["detail"].lower()

    @pytest.mark.asyncio
    async def test_long_request_with_extended_timeout_succeeds(
        self, mock_app: MagicMock, mock_request: MagicMock
    ):
        """Test that long request succeeds with extended timeout."""
        # Arrange
        extended_middleware = TimeoutMiddleware(mock_app, timeout=3)
        mock_response = MagicMock()

        async def slow_call_next(request):
            await asyncio.sleep(1.5)
            return mock_response

        # Act
        response = await extended_middleware.dispatch(mock_request, slow_call_next)

        # Assert
        assert response == mock_response
        assert response.status_code != 504

    @pytest.mark.asyncio
    async def test_preserves_response_when_no_timeout(
        self, middleware: TimeoutMiddleware, mock_request: MagicMock
    ):
        """Test that original response is preserved when no timeout occurs."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Custom": "Header"}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response.status_code == 200
        assert response.headers["Custom"] == "Header"
