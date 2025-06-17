from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Nutrition Profile
    target_calories = Column(Float)
    target_protein = Column(Float)  # in grams
    target_carbs = Column(Float)    # in grams
    target_fats = Column(Float)     # in grams
    
    # User Preferences
    height = Column(Float)          # in cm
    weight = Column(Float)          # in kg
    age = Column(Integer)
    activity_level = Column(String)  # e.g., "sedentary", "moderate", "active"
    dietary_restrictions = Column(String)  # comma-separated list of restrictions

    food_logs = relationship("FoodLog", back_populates="user")
