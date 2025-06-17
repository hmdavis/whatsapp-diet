from typing import Optional
from pydantic import BaseModel, Field


class MacroNutrients(BaseModel):
    """Macronutrient information."""
    calories: float = Field(..., ge=0, description="Calories")
    protein: float = Field(..., ge=0, description="Protein in grams")
    carbs: float = Field(..., ge=0, description="Carbohydrates in grams") 
    fats: float = Field(..., ge=0, description="Fats in grams")


class NutritionInfo(BaseModel):
    """Detailed nutrition information for a food item."""
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fats: float = Field(..., ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sugar: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    confidence: float = Field(..., ge=0, le=1, description="AI confidence score 0-1")