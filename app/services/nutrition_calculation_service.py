"""Service for calculating nutrition totals and progress."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.food_log import FoodLog
from app.schemas.nutrition import MacroNutrients
from app.schemas.user import DailyProgress, NutritionProfile


class NutritionCalculationService:
    """Handles nutrition calculations and progress tracking."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_daily_totals(self, user_id: int, date: datetime.date = None) -> MacroNutrients:
        """
        Calculate total nutrition for a specific day.
        
        Args:
            user_id: User ID
            date: Date to calculate for (defaults to today)
            
        Returns:
            MacroNutrients with daily totals
        """
        if date is None:
            date = datetime.now(timezone.utc).date()
            
        stmt = select(
            func.sum(FoodLog.calories).label('total_calories'),
            func.sum(FoodLog.protein).label('total_protein'),
            func.sum(FoodLog.carbs).label('total_carbs'),
            func.sum(FoodLog.fats).label('total_fats')
        ).where(
            FoodLog.user_id == user_id,
            func.date(FoodLog.created_at) == date
        )
        
        result = await self.db.execute(stmt)
        daily_totals = result.first()
        
        return MacroNutrients(
            calories=float(daily_totals.total_calories or 0),
            protein=float(daily_totals.total_protein or 0),
            carbs=float(daily_totals.total_carbs or 0),
            fats=float(daily_totals.total_fats or 0)
        )
    
    def calculate_meal_totals(self, food_logs: List[FoodLog]) -> MacroNutrients:
        """
        Calculate total nutrition for a meal from food log entries.
        
        Args:
            food_logs: List of FoodLog entries
            
        Returns:
            MacroNutrients with meal totals
        """
        return MacroNutrients(
            calories=sum(log.calories for log in food_logs),
            protein=sum(log.protein for log in food_logs),
            carbs=sum(log.carbs for log in food_logs),
            fats=sum(log.fats for log in food_logs)
        )
    
    def calculate_daily_progress(
        self, 
        consumed: MacroNutrients, 
        targets: MacroNutrients
    ) -> DailyProgress:
        """
        Calculate daily nutrition progress.
        
        Args:
            consumed: Consumed nutrients
            targets: Target nutrients
            
        Returns:
            DailyProgress with consumed, targets, and remaining
        """
        remaining = MacroNutrients(
            calories=max(0, targets.calories - consumed.calories),
            protein=max(0, targets.protein - consumed.protein),
            carbs=max(0, targets.carbs - consumed.carbs),
            fats=max(0, targets.fats - consumed.fats)
        )
        
        return DailyProgress(
            consumed=consumed,
            targets=targets,
            remaining=remaining
        )
    
    def calculate_macro_percentage(self, consumed: float, target: float) -> int:
        """Calculate percentage of macro consumed vs target."""
        if target <= 0:
            return 0
        return int((consumed / target) * 100)
    
    def generate_recommendations(self, progress: DailyProgress) -> List[str]:
        """
        Generate nutrition recommendations based on daily progress.
        
        Args:
            progress: Daily progress data
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        remaining = progress.remaining
        
        if remaining.calories > 0:
            if remaining.protein > 0:
                recommendations.append(
                    f"You still need {remaining.protein:.1f}g of protein. "
                    "Consider adding lean protein sources."
                )
            
            if remaining.carbs > 0:
                recommendations.append(
                    f"You have {remaining.carbs:.1f}g of carbs remaining. "
                    "Good for energy before workouts."
                )
            
            if remaining.fats > 0:
                recommendations.append(
                    f"You can add {remaining.fats:.1f}g of healthy fats "
                    "to your next meal."
                )
        else:
            recommendations.append(
                "You've reached your daily calorie target. "
                "Consider lighter options for remaining meals."
            )
        
        return recommendations