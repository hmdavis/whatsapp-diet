"""User-related exception classes."""

from .base import DietTrackerException


class UserNotFoundError(DietTrackerException):
    """Raised when user is not found."""
    
    def __init__(self, phone_number: str = None):
        message = f"User not found: {phone_number}" if phone_number else "User not found"
        super().__init__(message, "USER_NOT_FOUND")


class InvalidUserDataError(DietTrackerException):
    """Raised when user data is invalid."""
    
    def __init__(self, message: str = "Invalid user data"):
        super().__init__(message, "INVALID_USER_DATA")