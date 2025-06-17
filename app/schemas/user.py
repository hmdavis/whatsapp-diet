from typing import Optional
from pydantic import BaseModel, Field
from .nutrition import MacroNutrients


class NutritionProfile(BaseModel):
    """User's nutritional goals and profile."""
    target_calories: Optional[float] = Field(None, ge=0)
    target_protein: Optional[float] = Field(None, ge=0)
    target_carbs: Optional[float] = Field(None, ge=0)
    target_fats: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    age: Optional[int] = Field(None, ge=0)
    activity_level: Optional[str] = Field(None)
    goal: Optional[str] = Field(None, description="Weight loss, gain, maintenance")


class DailyProgress(BaseModel):
    """User's daily nutrition progress."""
    consumed: MacroNutrients
    targets: MacroNutrients
    remaining: MacroNutrients
    
    @property
    def calories_percentage(self) -> float:
        """Calculate percentage of daily calories consumed."""
        if self.targets.calories == 0:
            return 0
        return (self.consumed.calories / self.targets.calories) * 100


class UserResponse(BaseModel):
    """User information response."""
    id: int
    phone_number: str
    nutrition_profile: Optional[NutritionProfile] = None
    created_at: str