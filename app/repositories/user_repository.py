"""User repository for user-specific database operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository
from app.exceptions.user import UserNotFoundError


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
    
    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """
        Get user by phone number.
        
        Args:
            phone_number: User's phone number
            
        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.phone_number == phone_number)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_phone_number_or_raise(self, phone_number: str) -> User:
        """
        Get user by phone number or raise exception.
        
        Args:
            phone_number: User's phone number
            
        Returns:
            User instance
            
        Raises:
            UserNotFoundError: If user is not found
        """
        user = await self.get_by_phone_number(phone_number)
        if not user:
            raise UserNotFoundError(phone_number)
        return user
    
    async def create_user(self, phone_number: str, **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            phone_number: User's phone number
            **kwargs: Additional user attributes
            
        Returns:
            Created User instance
        """
        user = User(phone_number=phone_number, **kwargs)
        return await self.create(user)
    
    async def update_nutrition_targets(
        self,
        user_id: int,
        target_calories: Optional[float] = None,
        target_protein: Optional[float] = None,
        target_carbs: Optional[float] = None,
        target_fats: Optional[float] = None
    ) -> User:
        """
        Update user's nutrition targets.
        
        Args:
            user_id: User ID
            target_calories: Target calories per day
            target_protein: Target protein in grams
            target_carbs: Target carbs in grams
            target_fats: Target fats in grams
            
        Returns:
            Updated User instance
            
        Raises:
            UserNotFoundError: If user is not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        if target_calories is not None:
            user.target_calories = target_calories
        if target_protein is not None:
            user.target_protein = target_protein
        if target_carbs is not None:
            user.target_carbs = target_carbs
        if target_fats is not None:
            user.target_fats = target_fats
        
        return await self.update(user)