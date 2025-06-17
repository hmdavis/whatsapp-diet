"""Service for formatting WhatsApp/SMS responses."""

from typing import List
from app.models.food_log import FoodLog
from app.schemas.nutrition import MacroNutrients
from app.schemas.user import DailyProgress


class ResponseFormattingService:
    """Formats responses for WhatsApp/SMS messages."""
    
    def format_food_log_response(
        self,
        food_logs: List[FoodLog],
        meal_totals: MacroNutrients,
        daily_progress: DailyProgress,
        recommendations: List[str]
    ) -> str:
        """
        Format a comprehensive food log response.
        
        Args:
            food_logs: List of logged food items
            meal_totals: Total nutrition for this meal
            daily_progress: User's daily progress
            recommendations: List of recommendations
            
        Returns:
            Formatted response string
        """
        response_parts = []
        
        # Header
        response_parts.append("Logged your meal! Here's the breakdown:\n")
        
        # Individual items
        for food_log in food_logs:
            item_text = f"• {food_log.normalized_title}:\n"
            item_text += f"  Calories: {food_log.calories:.0f}\n"
            item_text += f"  Protein: {food_log.protein:.1f}g\n"
            item_text += f"  Carbs: {food_log.carbs:.1f}g\n"
            item_text += f"  Fats: {food_log.fats:.1f}g\n"
            
            if hasattr(food_log, 'notes') and food_log.notes:
                item_text += f"  Note: {food_log.notes}\n"
            
            response_parts.append(item_text)
        
        # Meal totals
        meal_text = f"Total for this meal:\n"
        meal_text += f"Calories: {meal_totals.calories:.0f}\n"
        meal_text += f"Protein: {meal_totals.protein:.1f}g\n"
        meal_text += f"Carbs: {meal_totals.carbs:.1f}g\n"
        meal_text += f"Fats: {meal_totals.fats:.1f}g\n"
        response_parts.append(meal_text)
        
        # Daily progress
        progress_text = self._format_daily_progress(daily_progress)
        response_parts.append(progress_text)
        
        # Recommendations
        if recommendations:
            rec_text = "Recommendations:\n"
            for rec in recommendations:
                rec_text += f"• {rec}\n"
            response_parts.append(rec_text)
        
        return "\n".join(response_parts).strip()
    
    def _format_daily_progress(self, progress: DailyProgress) -> str:
        """Format daily progress section."""
        consumed = progress.consumed
        targets = progress.targets
        
        progress_text = "Today's Progress:\n"
        
        # Calories
        cal_pct = self._calculate_percentage(consumed.calories, targets.calories)
        progress_text += f"Calories: {consumed.calories:.0f}/{targets.calories:.0f} ({cal_pct}%)\n"
        
        # Protein
        protein_pct = self._calculate_percentage(consumed.protein, targets.protein)
        progress_text += f"Protein: {consumed.protein:.1f}g/{targets.protein:.1f}g ({protein_pct}%)\n"
        
        # Carbs
        carbs_pct = self._calculate_percentage(consumed.carbs, targets.carbs)
        progress_text += f"Carbs: {consumed.carbs:.1f}g/{targets.carbs:.1f}g ({carbs_pct}%)\n"
        
        # Fats
        fats_pct = self._calculate_percentage(consumed.fats, targets.fats)
        progress_text += f"Fats: {consumed.fats:.1f}g/{targets.fats:.1f}g ({fats_pct}%)\n"
        
        return progress_text
    
    def _calculate_percentage(self, consumed: float, target: float) -> int:
        """Calculate percentage, handling zero targets."""
        if target <= 0:
            return 0
        return int((consumed / target) * 100)
    
    def format_error_response(self, error_message: str) -> str:
        """Format error response for users."""
        return f"Sorry, an error occurred: {error_message}"
    
    def format_user_not_found_response(self) -> str:
        """Format response when user is not found."""
        return "User not found. Please set up your profile first."