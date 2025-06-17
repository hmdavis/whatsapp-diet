from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.services.openai_service import OpenAIService
from app.models.user import User
from app.models.food_log import FoodLog
from app.services.food_log_service import FoodLogService
from typing import Dict, Any, Optional, cast, Union
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import Response
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook/message")
async def handle_message(
    Body: str = Form(...),
    From: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle incoming WhatsApp/SMS messages
    """
    try:
        # Parse the incoming message
        message = Body
        # Remove 'whatsapp:' prefix if present
        phone_number = From.replace('whatsapp:', '')
        
        # Get or create user
        stmt = select(User).where(User.phone_number == phone_number)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Create a TwiML response for user not found
            resp = MessagingResponse()
            resp.message("User not found. Please set up your profile first.")
            return Response(content=str(resp), media_type="application/xml")
        
        # Initialize services
        openai_service = OpenAIService()
        food_log_service = FoodLogService(db)
        
        # Get user profile data, handling None values
        def get_float_value(value: Optional[Union[float, Any]]) -> Optional[float]:
            if value is None:
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        user_profile = {
            "target_calories": get_float_value(user.target_calories),
            "target_protein": get_float_value(user.target_protein),
            "target_carbs": get_float_value(user.target_carbs),
            "target_fats": get_float_value(user.target_fats)
        }
        
        # Create a TwiML response
        resp = MessagingResponse()
        
        # Check if it's a question or a food entry
        question_words = ["how", "what", "why", "when", "where", "can", "could", "would", "should", "do", "does", "did", "is", "are", "was", "were", "will", "have", "has", "had"]
        is_question = any([
            message.lower().startswith(tuple(question_words)),
            "?" in message,
            "recommend" in message.lower(),
            "suggest" in message.lower(),
            "advice" in message.lower(),
        ])
        
        if is_question:
            # Get recent food logs summary for context
            food_logs_summary = await food_log_service.get_recent_food_logs_summary(user.__dict__["id"])
            
            # Handle question with food log context
            response_text = await openai_service.analyze_diet_question(
                message,
                user_profile,
                food_logs_summary
            )
        else:
            print("Adding food log")
            # Handle food entry - get the primary key value
            user_id = user.__dict__["id"]  # Access the actual value from the instance dict
            food_logs = await food_log_service.create_food_log(user_id, message)
            
            # Get today's total nutrition
            today = datetime.now(timezone.utc).date()
            stmt = select(
                func.sum(FoodLog.calories).label('total_calories'),
                func.sum(FoodLog.protein).label('total_protein'),
                func.sum(FoodLog.carbs).label('total_carbs'),
                func.sum(FoodLog.fats).label('total_fats')
            ).where(
                FoodLog.user_id == user_id,
                func.date(FoodLog.created_at) == today
            )
            result = await db.execute(stmt)
            daily_totals = result.first()
            
            # Generate response
            response_text = f"Logged your meal! Here's the breakdown:\n\n"
            
            # Add individual items
            for food_log in food_logs:
                response_text += f"• {food_log.normalized_title}:\n"
                response_text += f"  Calories: {food_log.calories}\n"
                response_text += f"  Protein: {food_log.protein}g\n"
                response_text += f"  Carbs: {food_log.carbs}g\n"
                response_text += f"  Fats: {food_log.fats}g\n"
                if food_log.notes is not None:
                    response_text += f"  Note: {food_log.notes}\n"
                response_text += "\n"
            
            # Add total nutrition for this meal
            meal_calories = sum(log.calories for log in food_logs)
            meal_protein = sum(log.protein for log in food_logs)
            meal_carbs = sum(log.carbs for log in food_logs)
            meal_fats = sum(log.fats for log in food_logs)
            
            response_text += f"Total for this meal:\n"
            response_text += f"Calories: {meal_calories}\n"
            response_text += f"Protein: {meal_protein}g\n"
            response_text += f"Carbs: {meal_carbs}g\n"
            response_text += f"Fats: {meal_fats}g\n\n"
            
            # Add daily progress
            daily_calories = float(daily_totals.total_calories if daily_totals and daily_totals.total_calories is not None else 0)
            daily_protein = float(daily_totals.total_protein if daily_totals and daily_totals.total_protein is not None else 0)
            daily_carbs = float(daily_totals.total_carbs if daily_totals and daily_totals.total_carbs is not None else 0)
            daily_fats = float(daily_totals.total_fats if daily_totals and daily_totals.total_fats is not None else 0)
            
            target_calories = float(user_profile['target_calories'] or 0)
            target_protein = float(user_profile['target_protein'] or 0)
            target_carbs = float(user_profile['target_carbs'] or 0)
            target_fats = float(user_profile['target_fats'] or 0)
            
            response_text += f"Today's Progress:\n"
            response_text += f"Calories: {daily_calories}/{target_calories} ({int(daily_calories/target_calories*100 if target_calories > 0 else 0)}%)\n"
            response_text += f"Protein: {daily_protein}g/{target_protein}g ({int(daily_protein/target_protein*100 if target_protein > 0 else 0)}%)\n"
            response_text += f"Carbs: {daily_carbs}g/{target_carbs}g ({int(daily_carbs/target_carbs*100 if target_carbs > 0 else 0)}%)\n"
            response_text += f"Fats: {daily_fats}g/{target_fats}g ({int(daily_fats/target_fats*100 if target_fats > 0 else 0)}%)\n\n"
            
            # Add recommendations based on remaining macros
            remaining_calories = target_calories - daily_calories
            remaining_protein = target_protein - daily_protein
            remaining_carbs = target_carbs - daily_carbs
            remaining_fats = target_fats - daily_fats
            
            response_text += "Recommendations:\n"
            if remaining_calories > 0:
                if remaining_protein > 0:
                    response_text += f"• You still need {remaining_protein}g of protein. Consider adding lean protein sources.\n"
                if remaining_carbs > 0:
                    response_text += f"• You have {remaining_carbs}g of carbs remaining. Good for energy before workouts.\n"
                if remaining_fats > 0:
                    response_text += f"• You can add {remaining_fats}g of healthy fats to your next meal.\n"
            else:
                response_text += "• You've reached your daily calorie target. Consider lighter options for remaining meals.\n"
        
        # Add the response to TwiML
        resp.message(response_text)
        
        # Return the TwiML response
        return Response(content=str(resp), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        # Create a TwiML response for the error
        resp = MessagingResponse()
        resp.message(f"Sorry, an error occurred: {str(e)}")
        return Response(content=str(resp), media_type="application/xml") 