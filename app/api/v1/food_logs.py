from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_food_log_service
from app.services.food_log_service import FoodLogService
from app.schemas.food_log import FoodLogResponse, FoodLogCreate, FoodLogSummary
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{user_id}", response_model=List[FoodLogResponse])
async def create_food_log(
    user_id: int,
    food_data: FoodLogCreate,
    food_log_service: FoodLogService = Depends(get_food_log_service)
) -> List[FoodLogResponse]:
    """Create new food log entries."""
    try:
        food_logs = await food_log_service.create_food_log(user_id, food_data.message)
        return [FoodLogResponse.from_orm(log) for log in food_logs]
    except Exception as e:
        logger.error(f"Error creating food log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=List[FoodLogResponse])
async def get_user_food_logs(
    user_id: int,
    limit: int = 10,
    food_log_service: FoodLogService = Depends(get_food_log_service)
) -> List[FoodLogResponse]:
    """Get recent food logs for a user."""
    try:
        food_logs = await food_log_service.get_user_food_logs(user_id, limit)
        return [FoodLogResponse.from_orm(log) for log in food_logs]
    except Exception as e:
        logger.error(f"Error getting user food logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 