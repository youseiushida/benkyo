"""Exception types for benkyo. Each maps to a CLI error code."""


class BenkyoError(Exception):
    """Base class for all benkyo errors."""

    code: str = "error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(BenkyoError):
    """Entity not found for the given id."""

    code = "not_found"


class ConflictError(BenkyoError):
    """Duplicate id or foreign-key conflict."""

    code = "conflict"


class InvalidArgError(BenkyoError):
    """Invalid argument or malformed value."""

    code = "invalid_arg"
