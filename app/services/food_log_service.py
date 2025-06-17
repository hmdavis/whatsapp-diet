from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.food_log import FoodLog
from app.services.openai_service import OpenAIService
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FoodLogService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_service = OpenAIService()

    async def create_food_log(self, user_id: int, food_description: str) -> List[FoodLog]:
        """Create food log entries for each food item in the description."""
        try:
            # Get AI analysis
            analysis = await self.openai_service.analyze_food_entry(food_description)
            
            # Create food log entries for each item
            food_logs = []
            for item in analysis["items"]:
                food_log = FoodLog(
                    user_id=user_id,
                    food_description=food_description,
                    normalized_title=item["normalized_title"],
                    meal_type=analysis["meal_type"],
                    calories=item["nutrition"]["calories"],
                    protein=item["nutrition"]["protein"],
                    carbs=item["nutrition"]["carbs"],
                    fats=item["nutrition"]["fats"],
                    confidence_score=item["confidence_score"],
                    notes=item.get("notes") or analysis.get("notes")
                )
                self.db.add(food_log)
                food_logs.append(food_log)
            
            await self.db.commit()
            
            # Refresh all food logs to get their IDs
            for food_log in food_logs:
                await self.db.refresh(food_log)
            
            return food_logs
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating food logs: {str(e)}")
            raise

    async def get_user_food_logs(self, user_id: int, limit: int = 10) -> List[FoodLog]:
        """Get recent food logs for a user."""
        try:
            stmt = (
                select(FoodLog)
                .where(FoodLog.user_id == user_id)
                .order_by(FoodLog.created_at.desc())
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            return [row[0] for row in result.all()]
        except Exception as e:
            logger.error(f"Error getting user food logs: {str(e)}")
            raise

    async def get_recent_food_logs_summary(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get a summary of recent food logs for a user, including daily totals and trends."""
        try:
            # Calculate the date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get all food logs within the date range
            stmt = (
                select(FoodLog)
                .where(
                    FoodLog.user_id == user_id,
                    FoodLog.created_at >= start_date,
                    FoodLog.created_at <= end_date
                )
                .order_by(FoodLog.created_at.desc())
            )
            result = await self.db.execute(stmt)
            food_logs = [row[0] for row in result.all()]
            
            # Calculate daily totals
            daily_totals = {}
            for log in food_logs:
                date = log.created_at.date()
                if date not in daily_totals:
                    daily_totals[date] = {
                        "calories": 0,
                        "protein": 0,
                        "carbs": 0,
                        "fats": 0,
                        "items": []
                    }
                
                daily_totals[date]["calories"] += log.calories
                daily_totals[date]["protein"] += log.protein
                daily_totals[date]["carbs"] += log.carbs
                daily_totals[date]["fats"] += log.fats
                daily_totals[date]["items"].append({
                    "title": log.normalized_title,
                    "meal_type": log.meal_type,
                    "calories": log.calories,
                    "protein": log.protein,
                    "carbs": log.carbs,
                    "fats": log.fats
                })
            
            # Calculate averages
            total_days = len(daily_totals)
            if total_days > 0:
                avg_calories = sum(day["calories"] for day in daily_totals.values()) / total_days
                avg_protein = sum(day["protein"] for day in daily_totals.values()) / total_days
                avg_carbs = sum(day["carbs"] for day in daily_totals.values()) / total_days
                avg_fats = sum(day["fats"] for day in daily_totals.values()) / total_days
            else:
                avg_calories = avg_protein = avg_carbs = avg_fats = 0
            
            # Get most common meal types
            meal_types = {}
            for log in food_logs:
                meal_types[log.meal_type] = meal_types.get(log.meal_type, 0) + 1
            
            return {
                "daily_logs": daily_totals,
                "averages": {
                    "calories": avg_calories,
                    "protein": avg_protein,
                    "carbs": avg_carbs,
                    "fats": avg_fats
                },
                "meal_type_distribution": meal_types,
                "total_logs": len(food_logs),
                "days_analyzed": total_days
            }
            
        except Exception as e:
            logger.error(f"Error getting food logs summary: {str(e)}")
            raise 