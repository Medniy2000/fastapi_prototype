from typing import List, Optional


class AppException(Exception):
    """Base exception for all application errors"""

    def __init__(
        self,
        message: str,
        details: Optional[List[dict]] = None,
        extra: Optional[dict] = None,
    ) -> None:
        details_ = details
        if details_ is None:
            details_ = []

        extra_ = extra
        if extra_ is None:
            extra_ = {}

        self.message = message
        self.details = details_
        self.extra = extra_
        super().__init__(self.message)


class ValidationError(AppException):
    """Invalid input or data validation failed"""

    pass


class NotFoundError(AppException):
    """Resource not found"""

    pass


class AlreadyExistsError(AppException):
    """Resource already exists"""

    pass


class AuthenticationError(AppException):
    """Authentication failed"""

    pass


class AuthorizationError(AppException):
    """Insufficient permissions"""

    pass
