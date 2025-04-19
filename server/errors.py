import uuid
from typing import Optional
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class BaseError(HTTPException):
    """Base class for custom exceptions."""

    def __init__(
        self, status_code: int, title: str, detail: str, context: Optional[str] = None
    ):
        # Ensure detail is always a string
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"X-Error": title},
        )
        self.title = title
        self.context = context


class BadRequestError(BaseError):
    """Custom exception for bad request errors."""

    def __init__(
        self,
        detail: str = "Bad request",
        context: Optional[str] = None,
        extra_info: str = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="http_exception",
            detail=detail,
            context=context,
        )
        self.extra_info = extra_info


class NotFoundError(BaseError):
    """Custom exception for not found errors."""

    def __init__(
        self, detail: str, context: Optional[str] = None, extra_info: str = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="http_exception",
            detail=detail,
            context=context,
        )
        self.extra_info = extra_info


class AlreadyExistsError(BaseError):
    """Custom exception for already exists errors."""

    def __init__(
        self, detail: str, context: Optional[str] = None, extra_info: str = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="http_exception",
            detail=detail,
            context=context,
        )
        self.extra_info = extra_info


class ValidationError(BaseError):
    """Custom exception for validation errors."""

    def __init__(
        self,
        detail: str = "Invalid input",
        context: Optional[str] = None,
        extra_info: str = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="http_exception",
            detail=detail,
            context=context,
        )
        self.extra_info = extra_info


class UnauthorizedError(BaseError):
    """Custom exception for unauthorized access."""

    def __init__(
        self,
        detail: str = "Unauthorized access",
        context: Optional[str] = None,
        extra_info: str = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="http_exception",
            detail=detail,
            context=context,
        )
        self.extra_info = extra_info


class ForbiddenError(BaseError):
    """Custom exception for forbidden access."""

    def __init__(
        self,
        detail: str = "Forbidden access",
        context: Optional[str] = None,
        extra_info: str = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="http_exception",
            detail=detail,
            context=context,
        )
        self.extra_info = extra_info


def register_exceptions(app):
    """Register exception handlers for custom exceptions."""

    def format_error_response(exc, status_code):
        return {
            "result": "error",
            "errors": [
                {
                    "id": str(uuid.uuid4()),  # Generate a unique ID for the error
                    "status": status_code,
                    "title": exc.title if hasattr(exc, "title") else "http_exception",
                    "detail": str(exc.detail) if hasattr(exc, "detail") else str(exc),
                    "context": exc.context if hasattr(exc, "context") else None,
                }
            ],
        }

    async def validation_exception_handler(_: Request, exc: ValidationError):
        content = format_error_response(exc, status.HTTP_422_UNPROCESSABLE_ENTITY)
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    async def bad_request_exception_handler(_: Request, exc: BadRequestError):
        content = format_error_response(exc, status.HTTP_400_BAD_REQUEST)
        return JSONResponse(content=content, status_code=status.HTTP_400_BAD_REQUEST)

    async def not_found_exception_handler(_: Request, exc: NotFoundError):
        content = format_error_response(exc, status.HTTP_404_NOT_FOUND)
        return JSONResponse(content=content, status_code=status.HTTP_404_NOT_FOUND)

    async def unauthorized_exception_handler(_: Request, exc: UnauthorizedError):
        content = format_error_response(exc, status.HTTP_401_UNAUTHORIZED)
        return JSONResponse(content=content, status_code=status.HTTP_401_UNAUTHORIZED)

    async def forbidden_exception_handler(_: Request, exc: ForbiddenError):
        content = format_error_response(exc, status.HTTP_403_FORBIDDEN)
        return JSONResponse(content=content, status_code=status.HTTP_403_FORBIDDEN)

    app.exception_handler(ValidationError)(validation_exception_handler)
    app.exception_handler(BadRequestError)(bad_request_exception_handler)
    app.exception_handler(NotFoundError)(not_found_exception_handler)
    app.exception_handler(UnauthorizedError)(unauthorized_exception_handler)
    app.exception_handler(ForbiddenError)(forbidden_exception_handler)
    app.exception_handler(RequestValidationError)(validation_exception_handler)
