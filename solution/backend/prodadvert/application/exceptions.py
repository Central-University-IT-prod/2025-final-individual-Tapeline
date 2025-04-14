"""Contains app-level exceptions."""


class AppException(Exception):
    """Base exception for all app exceptions."""
    def __init__(self, *args, extra: dict | None = None, **kwargs) -> None:
        super().__init__(*args)
        self.extra = extra or {}
        self.code = kwargs.get("code")


class NotFoundException(AppException):
    """Raised when something is not found."""


class AlreadyExistsException(AppException):
    """Raised when tried to create something that exists already."""


class InvalidDataException(AppException):
    """Raised when invalid data inputted."""


class ForbiddenException(AppException):
    """Raised when an action is forbidden."""
