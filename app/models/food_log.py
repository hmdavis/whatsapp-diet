from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Food Entry Details
    food_description = Column(String)  # Original text from user
    normalized_title = Column(String)  # Normalized, presentable title (e.g., "Cold Brew with Almond Milk")
    meal_type = Column(String)        # e.g., "breakfast", "lunch", "dinner", "snack", "drink"
    
    # Nutritional Information
    calories = Column(Float)
    protein = Column(Float)  # in grams
    carbs = Column(Float)    # in grams
    fats = Column(Float)     # in grams
    
    # AI Analysis
    confidence_score = Column(Float)  # AI's confidence in the analysis
    notes = Column(String)            # Additional notes or clarifications
    
    # Relationships
    user = relationship("User", back_populates="food_logs") 