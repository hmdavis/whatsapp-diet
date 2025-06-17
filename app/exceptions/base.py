"""Base exception classes for the diet tracker application."""


class DietTrackerException(Exception):
    """Base exception for all diet tracker errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)