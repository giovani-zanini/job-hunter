"""Global exception handlers for FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared import exceptions


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers for the application."""

    @app.exception_handler(exceptions.AppException)
    async def app_exception_handler(
        request: Request, exc: exceptions.AppException
    ) -> JSONResponse:
        """Handle all application exceptions."""
        content = {
            "detail": exc.detail,
            "type": exc.__class__.__name__,
        }
        if exc.extra:
            content.update(exc.extra)

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )
