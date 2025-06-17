from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.food_log_service import FoodLogService
from app.models.food_log import FoodLog
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{user_id}/food-logs", response_model=FoodLog)
async def create_food_log(
    user_id: int,
    food_description: str,
    db: AsyncSession = Depends(get_db)
) -> FoodLog:
    """Create a new food log entry."""
    try:
        food_log_service = FoodLogService(db)
        return await food_log_service.create_food_log(user_id, food_description)
    except Exception as e:
        logger.error(f"Error creating food log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/food-logs", response_model=List[FoodLog])
async def get_user_food_logs(
    user_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
) -> List[FoodLog]:
    """Get recent food logs for a user."""
    try:
        food_log_service = FoodLogService(db)
        return await food_log_service.get_user_food_logs(user_id, limit)
    except Exception as e:
        logger.error(f"Error getting user food logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 