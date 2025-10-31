"""
Request Context Middleware Module

This module defines custom middleware classes for the FastAPI application.
It includes middleware for handling timeouts and generating request IDs for each request.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import uuid
from typing import Any, Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to deal with long running requests."""

    def __init__(self, app: Any, timeout: int):
        """
        Initializes the TimeoutMiddleware with the given timeout value.

        Args:
            app (Any): The ASGI app.
            timeout (int): The timeout value in seconds.
        """
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Dispatches the request and handles timeouts.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable[[Request], Awaitable[Response]]): The next middleware or route handler.

        Returns:
            Response: The HTTP response.

        Raises:
            JSONResponse: If the request times out.
        """
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError:
            return JSONResponse({"detail": "Request timed out"}, status_code=504)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate a unique request ID for each request."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Dispatches the request and attaches a unique request ID to it.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable[[Request], Awaitable[Response]]): The next middleware or route handler.

        Returns:
            Response: The HTTP response with the request ID header.
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
