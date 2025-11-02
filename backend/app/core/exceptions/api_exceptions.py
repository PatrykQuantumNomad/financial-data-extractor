"""
API layer exception classes.

These exceptions are used exclusively in the API/endpoint layer.
They extend FastAPI's HTTPException and are used to return
proper HTTP responses to clients.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from enum import Enum

from fastapi import HTTPException, status


class ErrorType(Enum):
    """
    Enumeration of standardized URIs for error types based on HTTP status codes.

    This enum provides a centralized set of URIs corresponding to common HTTP error statuses,
    facilitating consistent and standardized error responses in accordance with
    [RFC 7807](https://tools.ietf.org/html/rfc7807) (Problem Details for HTTP APIs).
    """

    INTERNAL_SERVER_ERROR = "https://httpstatuses.com/500"
    BAD_REQUEST = "https://httpstatuses.com/400"
    NOT_FOUND = "https://httpstatuses.com/404"
    UNSUPPORTED_MEDIA_TYPE = "https://httpstatuses.com/415"
    FORBIDDEN = "https://httpstatuses.com/403"


class ApiError(HTTPException):
    """Base class for API layer exceptions."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str | None = "An unexpected error occurred.",
        title: str | None = "Internal Server Error",
        type_: str | None = None,
        instance: str | None = None,
    ) -> None:
        """
        Initialize the ApiError instance.

        Args:
            status_code (int): HTTP status code of the error.
            detail (Optional[str]): Detailed description of the error.
            title (Optional[str]): Short, human-readable summary of the error.
            type_ (Optional[str]): URI reference that identifies the problem type.
            instance (Optional[str]): URI reference that identifies the specific
                occurrence of the problem.
        """
        if title is None:
            title = self.__class__.__name__.replace("Error", "").replace("_", " ")
        type_ = type_ or f"https://httpstatuses.com/{status_code}"
        super().__init__(status_code=status_code, detail=detail)
        self.title = title
        self.type_ = type_
        self.instance = instance


class NotFoundError(ApiError):
    """Raised when a resource is not found."""

    def __init__(
        self,
        detail: str | None = "Resource not found",
        title: str | None = None,
        type_: str | None = None,
        instance: str | None = None,
    ) -> None:
        """
        Initialize NotFoundError instance.

        Args:
            detail (Optional[str]): Description of what was not found.
            title (Optional[str]): Short, human-readable summary.
            type_ (Optional[str]): URI reference that identifies the problem type.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        title = title or "Not Found"
        type_ = type_ or ErrorType.NOT_FOUND.value
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            title=title,
            type_=type_,
            instance=instance,
        )


class BadRequestError(ApiError):
    """Raised when a request is invalid."""

    def __init__(
        self,
        detail: str | None = "Bad request",
        title: str | None = None,
        type_: str | None = None,
        instance: str | None = None,
    ) -> None:
        """
        Initialize BadRequestError instance.

        Args:
            detail (Optional[str]): Description of the bad request.
            title (Optional[str]): Short, human-readable summary.
            type_ (Optional[str]): URI reference that identifies the problem type.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        title = title or "Bad Request"
        type_ = type_ or ErrorType.BAD_REQUEST.value
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            title=title,
            type_=type_,
            instance=instance,
        )


class ForbiddenError(ApiError):
    """Raised when an action is forbidden."""

    def __init__(
        self,
        detail: str | None = "Forbidden: insufficient roles.",
        title: str | None = None,
        type_: str | None = None,
        instance: str | None = None,
    ) -> None:
        """
        Initialize ForbiddenError instance.

        Args:
            detail (Optional[str]): Description of why the action is forbidden.
            title (Optional[str]): Short, human-readable summary.
            type_ (Optional[str]): URI reference that identifies the problem type.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        title = title or "Forbidden"
        type_ = type_ or ErrorType.FORBIDDEN.value
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            title=title,
            type_=type_,
            instance=instance,
        )


class InternalServerError(ApiError):
    """Raised when an internal server error occurs."""

    def __init__(
        self,
        detail: str | None = "An internal server error occurred.",
        title: str | None = None,
        type_: str | None = None,
        instance: str | None = None,
    ) -> None:
        """
        Initialize InternalServerError instance.

        Args:
            detail (Optional[str]): Description of the error.
            title (Optional[str]): Short, human-readable summary.
            type_ (Optional[str]): URI reference that identifies the problem type.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        title = title or "Internal Server Error"
        type_ = type_ or ErrorType.INTERNAL_SERVER_ERROR.value
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            title=title,
            type_=type_,
            instance=instance,
        )


# Keep existing JSON file errors for backward compatibility
class JSONFileError(ApiError):
    """Base exception for errors related to reading JSON files."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        title: str | None = "JSON File Error",
        type_: str | None = None,
        instance: str | None = None,
    ) -> None:
        """
        Initialize JSONFileError instance.

        Args:
            message (str): The error message.
            status_code (int): HTTP status code.
            title (Optional[str]): Short, human-readable summary.
            type_ (Optional[str]): URI reference that identifies the problem type.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        title = title or "JSON File Error"
        super().__init__(
            status_code=status_code,
            detail=message,
            title=title,
            type_=type_,
            instance=instance,
        )


class JSONFileNotFoundError(JSONFileError):
    """Raised when the JSON file is not found."""

    def __init__(self, filename: str, instance: str | None = None) -> None:
        """
        Initialize JSONFileNotFoundError instance.

        Args:
            filename (str): The name of the JSON file that was not found.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        message = f"JSON File '{filename}' not found."
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            title="JSON File Not Found",
            type_=ErrorType.NOT_FOUND.value,
            instance=instance,
        )


class JSONInvalidError(JSONFileError):
    """Raised when the JSON file is invalid."""

    def __init__(self, filename: str, error: str, instance: str | None = None) -> None:
        """
        Initialize JSONInvalidError instance.

        Args:
            filename (str): The name of the invalid JSON file.
            error (str): The error message describing why the JSON is invalid.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        message = f"JSON File '{filename}' is not a valid JSON. Error: {error}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Invalid JSON File",
            type_=ErrorType.BAD_REQUEST.value,
            instance=instance,
        )


class JSONInvalidEncodingError(JSONFileError):
    """Raised when the file encoding is not UTF-8."""

    def __init__(self, filename: str, error: str, instance: str | None = None) -> None:
        """
        Initialize JSONInvalidEncodingError instance.

        Args:
            filename (str): The name of the JSON file with invalid encoding.
            error (str): The error message describing the encoding issue.
            instance (Optional[str]): URI reference that identifies the specific occurrence.
        """
        message = f"JSON File '{filename}' does not use valid UTF-8 encoding. Error: {error}"
        super().__init__(
            message=message,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            title="Invalid JSON Encoding",
            type_=ErrorType.UNSUPPORTED_MEDIA_TYPE.value,
            instance=instance,
        )
