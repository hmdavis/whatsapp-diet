"""External service exception classes."""

from .base import DietTrackerException


class OpenAIServiceError(DietTrackerException):
    """Raised when OpenAI API calls fail."""
    
    def __init__(self, message: str = "OpenAI service error"):
        super().__init__(message, "OPENAI_SERVICE_ERROR")


class TwilioWebhookError(DietTrackerException):
    """Raised when Twilio webhook processing fails."""
    
    def __init__(self, message: str = "Twilio webhook processing error"):
        super().__init__(message, "TWILIO_WEBHOOK_ERROR")