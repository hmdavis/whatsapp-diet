"""Food-related exception classes."""

from .base import DietTrackerException


class FoodAnalysisError(DietTrackerException):
    """Raised when food analysis fails."""
    
    def __init__(self, message: str = "Failed to analyze food entry"):
        super().__init__(message, "FOOD_ANALYSIS_ERROR")


class InvalidFoodEntryError(DietTrackerException):
    """Raised when food entry data is invalid."""
    
    def __init__(self, message: str = "Invalid food entry data"):
        super().__init__(message, "INVALID_FOOD_ENTRY")