from typing import Optional
from fastapi import HTTPException, status


class BaseError(HTTPException):
    """Base class for custom exceptions."""

    def __init__(
        self, status_code: int, title: str, detail: str, context: Optional[str] = None
    ):
        error_detail = {
            "status": status_code,
            "title": title,
            "detail": detail,
            "context": context,
        }
        super().__init__(
            status_code=error_detail.get(
                "status", status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=error_detail,
            headers={"X-Error": title},
        )


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
