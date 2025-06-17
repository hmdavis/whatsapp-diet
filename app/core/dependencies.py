"""Dependency injection container for services."""

from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.food_log_repository import FoodLogRepository
from app.services.message_classification_service import MessageClassificationService
from app.services.nutrition_calculation_service import NutritionCalculationService
from app.services.response_formatting_service import ResponseFormattingService
from app.services.openai_service import OpenAIService
from app.services.food_log_service import FoodLogService


# Service factory functions with caching for stateless services

@lru_cache()
def get_message_classification_service() -> MessageClassificationService:
    """Get message classification service (cached singleton)."""
    return MessageClassificationService()


@lru_cache()
def get_response_formatting_service() -> ResponseFormattingService:
    """Get response formatting service (cached singleton)."""
    return ResponseFormattingService()


@lru_cache()
def get_openai_service() -> OpenAIService:
    """Get OpenAI service (cached singleton)."""
    return OpenAIService()


# Database-dependent services (not cached as they depend on DB session)

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_food_log_repository(db: AsyncSession = Depends(get_db)) -> FoodLogRepository:
    """Get food log repository."""
    return FoodLogRepository(db)


def get_nutrition_calculation_service(db: AsyncSession = Depends(get_db)) -> NutritionCalculationService:
    """Get nutrition calculation service."""
    return NutritionCalculationService(db)


def get_food_log_service(db: AsyncSession = Depends(get_db)) -> FoodLogService:
    """Get food log service."""
    return FoodLogService(db)