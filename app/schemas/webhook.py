from typing import Optional
from pydantic import BaseModel, Field


class WebhookRequest(BaseModel):
    """Twilio webhook request schema."""
    From: str = Field(..., description="Phone number sending the message")
    Body: str = Field(..., description="Message content")
    
    class Config:
        allow_population_by_field_name = True


class WebhookResponse(BaseModel):
    """Twilio webhook response schema."""
    message: str = Field(..., description="Response message to send back")
    
    def to_twiml(self) -> str:
        """Convert to TwiML format for Twilio response."""
        return f"<Response><Message>{self.message}</Message></Response>"