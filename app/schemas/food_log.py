from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .nutrition import NutritionInfo


class FoodAnalysisResult(BaseModel):
    """Result of AI food analysis."""
    food_name: str = Field(..., description="Normalized food name")
    quantity: str = Field(..., description="Estimated quantity")
    nutrition: NutritionInfo
    raw_analysis: str = Field(..., description="Raw AI response")


class FoodLogCreate(BaseModel):
    """Request to create a food log entry."""
    message: str = Field(..., description="User's food description message")


class FoodLogResponse(BaseModel):
    """Food log entry response."""
    id: int
    user_id: int
    food_name: str
    quantity: str
    calories: float
    protein: float
    carbs: float
    fats: float
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    confidence: float
    normalized_title: str
    raw_analysis: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class FoodLogSummary(BaseModel):
    """Summary of food logs for a day."""
    entries: List[FoodLogResponse]
    total_nutrition: NutritionInfo
    entry_count: int