class AppError(Exception):
    """Base application (domain) error. FastAPI-agnostic."""

    def __init__(self, message: str = "Application error") -> None:
        self.message = message
        super().__init__(message)


class ConflictError(AppError):
    """Raised when an entity already exists (e.g. email is taken)."""


class UnauthorizedError(AppError):
    """Raised when credentials are invalid (e.g. wrong password)."""


class ForbiddenError(AppError):
    """Raised when the user does not have permission to perform an action."""


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""


class ExternalServiceError(AppError):
    """Raised when an external service (e.g. OpenRouter) fails."""
