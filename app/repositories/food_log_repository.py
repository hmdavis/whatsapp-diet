"""Food log repository for food log database operations."""

from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.food_log import FoodLog
from app.repositories.base import BaseRepository


class FoodLogRepository(BaseRepository[FoodLog]):
    """Repository for FoodLog model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, FoodLog)
    
    async def get_by_user_id(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[FoodLog]:
        """
        Get food logs for a specific user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of FoodLog entries
        """
        stmt = (
            select(FoodLog)
            .where(FoodLog.user_id == user_id)
            .order_by(desc(FoodLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_by_user_and_date(
        self, 
        user_id: int, 
        date: datetime.date
    ) -> List[FoodLog]:
        """
        Get food logs for a specific user and date.
        
        Args:
            user_id: User ID
            date: Date to filter by
            
        Returns:
            List of FoodLog entries for the date
        """
        stmt = (
            select(FoodLog)
            .where(
                FoodLog.user_id == user_id,
                func.date(FoodLog.created_at) == date
            )
            .order_by(desc(FoodLog.created_at))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_recent_logs(
        self, 
        user_id: int, 
        days: int = 7
    ) -> List[FoodLog]:
        """
        Get recent food logs for a user.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of recent FoodLog entries
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(FoodLog)
            .where(
                FoodLog.user_id == user_id,
                FoodLog.created_at >= cutoff_date
            )
            .order_by(desc(FoodLog.created_at))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_daily_totals(
        self, 
        user_id: int, 
        date: datetime.date = None
    ) -> dict:
        """
        Get total nutrition for a specific day.
        
        Args:
            user_id: User ID
            date: Date to calculate for (defaults to today)
            
        Returns:
            Dictionary with nutrition totals
        """
        if date is None:
            date = datetime.now(timezone.utc).date()
        
        stmt = select(
            func.sum(FoodLog.calories).label('total_calories'),
            func.sum(FoodLog.protein).label('total_protein'),
            func.sum(FoodLog.carbs).label('total_carbs'),
            func.sum(FoodLog.fats).label('total_fats'),
            func.sum(FoodLog.fiber).label('total_fiber'),
            func.sum(FoodLog.sugar).label('total_sugar'),
            func.sum(FoodLog.sodium).label('total_sodium'),
            func.count(FoodLog.id).label('entry_count')
        ).where(
            FoodLog.user_id == user_id,
            func.date(FoodLog.created_at) == date
        )
        
        result = await self.db.execute(stmt)
        row = result.first()
        
        return {
            'total_calories': float(row.total_calories or 0),
            'total_protein': float(row.total_protein or 0),
            'total_carbs': float(row.total_carbs or 0),
            'total_fats': float(row.total_fats or 0),
            'total_fiber': float(row.total_fiber or 0),
            'total_sugar': float(row.total_sugar or 0),
            'total_sodium': float(row.total_sodium or 0),
            'entry_count': int(row.entry_count or 0)
        }
    
    async def create_food_log(
        self,
        user_id: int,
        food_name: str,
        quantity: str,
        calories: float,
        protein: float,
        carbs: float,
        fats: float,
        fiber: Optional[float] = None,
        sugar: Optional[float] = None,
        sodium: Optional[float] = None,
        confidence: float = 0.0,
        normalized_title: str = "",
        raw_analysis: str = "",
        notes: Optional[str] = None
    ) -> FoodLog:
        """
        Create a new food log entry.
        
        Args:
            user_id: User ID
            food_name: Name of the food
            quantity: Quantity consumed
            calories: Calories
            protein: Protein in grams
            carbs: Carbs in grams
            fats: Fats in grams
            fiber: Fiber in grams (optional)
            sugar: Sugar in grams (optional)
            sodium: Sodium in mg (optional)
            confidence: AI confidence score
            normalized_title: Normalized food name
            raw_analysis: Raw AI analysis
            notes: Additional notes (optional)
            
        Returns:
            Created FoodLog instance
        """
        food_log = FoodLog(
            user_id=user_id,
            food_name=food_name,
            quantity=quantity,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fats=fats,
            fiber=fiber,
            sugar=sugar,
            sodium=sodium,
            confidence=confidence,
            normalized_title=normalized_title,
            raw_analysis=raw_analysis,
            notes=notes
        )
        return await self.create(food_log)
    
    async def bulk_create_food_logs(self, food_logs: List[FoodLog]) -> List[FoodLog]:
        """
        Create multiple food log entries at once.
        
        Args:
            food_logs: List of FoodLog instances to create
            
        Returns:
            List of created FoodLog instances
        """
        self.db.add_all(food_logs)
        await self.db.commit()
        
        for food_log in food_logs:
            await self.db.refresh(food_log)
        
        return food_logs