"""Refactored webhook handler using service-oriented architecture."""

from fastapi import APIRouter, Depends, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

from app.schemas.nutrition import MacroNutrients
from app.core.dependencies import (
    get_user_repository,
    get_message_classification_service,
    get_nutrition_calculation_service,
    get_response_formatting_service,
    get_openai_service,
    get_food_log_service
)
from app.repositories.user_repository import UserRepository
from app.services.message_classification_service import MessageClassificationService
from app.services.nutrition_calculation_service import NutritionCalculationService
from app.services.response_formatting_service import ResponseFormattingService
from app.services.openai_service import OpenAIService
from app.services.food_log_service import FoodLogService
from app.exceptions import (
    UserNotFoundError, 
    FoodAnalysisError, 
    DietTrackerException
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/message")
async def handle_message(
    Body: str = Form(...),
    From: str = Form(...),
    user_repo: UserRepository = Depends(get_user_repository),
    message_classifier: MessageClassificationService = Depends(get_message_classification_service),
    nutrition_calculator: NutritionCalculationService = Depends(get_nutrition_calculation_service),
    response_formatter: ResponseFormattingService = Depends(get_response_formatting_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    food_log_service: FoodLogService = Depends(get_food_log_service)
):
    """Handle incoming WhatsApp/SMS messages with improved architecture."""
    try:
        
        # Clean phone number
        phone_number = From.replace('whatsapp:', '')
        
        # Get user or return error
        try:
            user = await user_repo.get_by_phone_number_or_raise(phone_number)
        except UserNotFoundError:
            return _create_twiml_response(response_formatter.format_user_not_found_response())
        
        # Extract user profile
        user_profile = _extract_user_profile(user)
        
        # Classify message
        message_type = message_classifier.classify_message(Body)
        
        if message_type == "question":
            response_text = await _handle_question(
                Body, user_profile, user.id, openai_service, food_log_service
            )
        else:
            response_text = await _handle_food_entry(
                Body, user, user_profile, food_log_service, 
                nutrition_calculator, response_formatter
            )
        
        return _create_twiml_response(response_text)
        
    except DietTrackerException as e:
        logger.error(f"Diet tracker error: {e.message}")
        error_response = response_formatter.format_error_response(e.message)
        return _create_twiml_response(error_response)
    
    except Exception as e:
        logger.error(f"Unexpected error handling message: {str(e)}")
        error_response = response_formatter.format_error_response(
            "An unexpected error occurred. Please try again."
        )
        return _create_twiml_response(error_response)


async def _handle_question(
    message: str,
    user_profile: dict,
    user_id: int,
    openai_service: OpenAIService,
    food_log_service: FoodLogService
) -> str:
    """Handle question messages."""
    try:
        # Get recent food logs for context
        food_logs_summary = await food_log_service.get_recent_food_logs_summary(user_id)
        
        # Get AI response
        response_text = await openai_service.analyze_diet_question(
            message, user_profile, food_logs_summary
        )
        
        return response_text
        
    except Exception as e:
        raise FoodAnalysisError(f"Failed to process question: {str(e)}")


async def _handle_food_entry(
    message: str,
    user,
    user_profile: dict,
    food_log_service: FoodLogService,
    nutrition_calculator: NutritionCalculationService,
    response_formatter: ResponseFormattingService
) -> str:
    """Handle food entry messages."""
    try:
        # Create food logs
        food_logs = await food_log_service.create_food_log(user.id, message)
        
        # Calculate meal totals
        meal_totals = nutrition_calculator.calculate_meal_totals(food_logs)
        
        # Get daily totals
        daily_consumed = await nutrition_calculator.get_daily_totals(user.id)
        
        # Create target nutrients from user profile
        daily_targets = MacroNutrients(
            calories=float(user_profile.get('target_calories', 0) or 0),
            protein=float(user_profile.get('target_protein', 0) or 0),
            carbs=float(user_profile.get('target_carbs', 0) or 0),
            fats=float(user_profile.get('target_fats', 0) or 0)
        )
        
        # Calculate daily progress
        daily_progress = nutrition_calculator.calculate_daily_progress(
            daily_consumed, daily_targets
        )
        
        # Generate recommendations
        recommendations = nutrition_calculator.generate_recommendations(daily_progress)
        
        # Format response
        return response_formatter.format_food_log_response(
            food_logs, meal_totals, daily_progress, recommendations
        )
        
    except Exception as e:
        raise FoodAnalysisError(f"Failed to process food entry: {str(e)}")


def _extract_user_profile(user) -> dict:
    """Extract user profile data with safe type conversion."""
    def get_float_value(value) -> float:
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
    return {
        "target_calories": get_float_value(user.target_calories),
        "target_protein": get_float_value(user.target_protein),
        "target_carbs": get_float_value(user.target_carbs),
        "target_fats": get_float_value(user.target_fats)
    }


def _create_twiml_response(message: str) -> Response:
    """Create TwiML response for Twilio."""
    resp = MessagingResponse()
    resp.message(message)
    return Response(content=str(resp), media_type="application/xml")