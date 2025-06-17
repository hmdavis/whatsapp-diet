from fastapi import APIRouter
from .webhook import router as webhook_router
from .food_logs import router as food_logs_router

api_router = APIRouter()
api_router.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
api_router.include_router(food_logs_router, prefix="/food-logs", tags=["food-logs"])