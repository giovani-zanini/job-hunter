"""Base exception classes for the application."""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for all application errors."""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: Optional[str] = None, **kwargs: Any) -> None:
        self.detail = detail or self.__class__.detail
        self.extra = kwargs
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Resource not found."""

    status_code = 404
    detail = "Resource not found"


class ConflictException(AppException):
    """Resource already exists or state conflict."""

    status_code = 409
    detail = "Resource conflict"


class ValidationException(AppException):
    """Business rule validation failed."""

    status_code = 422
    detail = "Validation error"


class BadRequestException(AppException):
    """Invalid request data."""

    status_code = 400
    detail = "Bad request"


class UnauthorizedException(AppException):
    """Authentication required."""

    status_code = 401
    detail = "Not authenticated"


class ForbiddenException(AppException):
    """Access denied."""

    status_code = 403
    detail = "Access forbidden"
