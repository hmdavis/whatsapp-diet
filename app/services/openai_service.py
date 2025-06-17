from openai import AsyncOpenAI
from app.core.config import get_settings
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
import json
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class FoodItem(BaseModel):
    normalized_title: str = Field(..., description="A clear, presentable title for the food item")
    nutrition: Dict[str, float] = Field(..., description="Nutritional information")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the analysis (0-1)")
    notes: Optional[str] = Field(None, description="Additional notes or clarifications")

class FoodAnalysis(BaseModel):
    meal_type: str = Field(..., description="Type of meal (breakfast, lunch, dinner, or snack)")
    items: List[FoodItem] = Field(..., description="List of food items in the meal")
    total_nutrition: Dict[str, float] = Field(..., description="Total nutritional information for all items")
    notes: Optional[str] = Field(None, description="Additional notes about the entire meal")

    @validator('meal_type')
    def validate_meal_type(cls, v):
        allowed_types = ['breakfast', 'lunch', 'dinner', 'snack', 'drink']
        if v.lower() not in allowed_types:
            raise ValueError(f'meal_type must be one of {allowed_types}')
        return v.lower()

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_food_entry(self, food_description: str) -> Dict[str, Any]:
        """
        Analyze a food entry using OpenAI's API to extract nutritional information.
        Handles multiple food items in a single message.
        """
        try:
            prompt = f"""Analyze the following food entry and provide a detailed nutritional breakdown.
            The entry may contain multiple food items or a single composite dish with multiple components.
            
            Food Entry: {food_description}
            
            PRODUCT GUIDELINES - INCORPORATE THESE PRINCIPLES IN YOUR ANALYSIS:
            
            FOODS TO EAT (Encourage these):
            • Meats, poultry & fish: steak, ground beef, ground bison, ground turkey, eggs, chicken breast, turkey breast, pork tenderloin, elk, venison, salmon, shrimp, cod, tilapia, tuna
            • Dairy: plain/greek yogurt, cottage cheese, milk, cheese
            • Grains: oatmeal, white rice, quinoa, popcorn
            • Vegetables: white potatoes, sweet potatoes, beets, spinach, broccoli, asparagus, tomatoes, peppers, mushrooms, cucumbers, zucchini, green beans, leafy salad greens
            • Fruits: apples, berries, bananas, oranges, grapes, watermelon, peaches, pears
            • Nuts & Seeds: walnuts, almonds, brazil nuts, macadamia nuts, flax seeds, sunflower seeds, chia seeds
            • Beans & Legumes: pinto beans, black beans, kidney beans, chickpeas, lentils
            • Oils/Fats: butter, ghee, olive oil, coconut oil, avocado oil, flaxseed oil
            
            FOODS TO LIMIT/AVOID (Note these in analysis):
            • Deep-fried foods
            • Added Sugars
            • Alcohol
            
            GENERAL PRINCIPLES:
            • Drink at least half your bodyweight [in ounces] of water daily
            • Consume 16-24oz of water first thing in the morning, every morning, to get a "jump start" on your hydration
            • Eliminate all beverages besides water, coffee/tea & protein shakes
            • Eat protein with every meal
            • Eat 1-3 servings fruit & 2-4 servings vegetables daily
            • Eat until satisfied, not "full"
            • Chew your food thoroughly
            • Spread your calories out over 3+ meals each day
            • Do all your food shopping after eating [never food shop when hungry]
            • Always Plan Ahead!
            
            Guidelines for Analysis:
            1. If the entry describes a single dish or meal (e.g., "a salad with chicken and vegetables", "a sandwich with turkey and cheese"),
               analyze it as ONE item with combined nutritional values.
            2. If the entry clearly lists separate items (e.g., "for breakfast I had a banana and a coffee"),
               break them into separate items.
            3. For composite dishes, consider all ingredients together and provide a single, comprehensive nutritional analysis.
            4. Use common sense to determine if items should be combined or separated.
            5. In the notes field, mention if the food aligns with our guidelines (e.g., "Great choice! This includes lean protein and vegetables" or "Consider limiting added sugars in this item").
            
            QUANTITY AND PORTION SIZE GUIDELINES:
            1. ALWAYS account for quantities mentioned in the food entry
            2. If a quantity is specified (e.g., "2 coronas", "3 cups rice", "1/2 avocado"), multiply the nutritional values by that quantity
            3. Common quantity indicators to look for:
               - Numbers: "2", "3", "1/2", "0.5", "1.5"
               - Units: "cups", "ounces", "oz", "pounds", "lbs", "grams", "g", "tablespoons", "tbsp", "teaspoons", "tsp"
               - Containers: "cans", "bottles", "servings", "pieces", "slices"
            4. For beverages, assume standard serving sizes if not specified:
               - Beer: 12 oz per serving
               - Wine: 5 oz per serving
               - Liquor: 1.5 oz per serving
               - Coffee/Tea: 8 oz per serving
            5. For common foods, use reasonable serving sizes if not specified:
               - Bananas: 1 medium banana
               - Apples: 1 medium apple
               - Eggs: 1 large egg
               - Bread: 1 slice
               - Rice: 1/2 cup cooked
            6. Calculate total nutrition by multiplying the base nutritional values by the quantity specified
            
            Provide your response in the following JSON format:
            {{
                "meal_type": "breakfast|lunch|dinner|snack|drink",
                "items": [
                    {{
                        "normalized_title": "A clear, presentable title for the food item or dish (include quantity if specified)",
                        "nutrition": {{
                            "calories": <number - account for quantity>,
                            "protein": <number in grams - account for quantity>,
                            "carbs": <number in grams - account for quantity>,
                            "fats": <number in grams - account for quantity>
                        }},
                        "confidence_score": <number between 0 and 1>,
                        "notes": "Any additional notes about this specific item or dish, including alignment with our guidelines and quantity calculations"
                    }},
                    // ... more items if they are truly separate
                ],
                "total_nutrition": {{
                    "calories": <sum of all items' calories>,
                    "protein": <sum of all items' protein>,
                    "carbs": <sum of all items' carbs>,
                    "fats": <sum of all items' fats>
                }},
                "notes": "Any additional notes about the entire meal, including guidance on how it fits with our principles"
            }}
            
            Examples:
            1. "I had a chicken salad with lettuce, tomatoes, and avocado" -> ONE item: "Chicken Salad with Vegetables"
            2. "For breakfast I had a banana and a coffee" -> TWO items: "Banana" and "Coffee"
            3. "A turkey sandwich with cheese, lettuce, and tomato" -> ONE item: "Turkey and Cheese Sandwich"
            4. "I had a bowl of oatmeal with berries and a side of yogurt" -> TWO items: "Oatmeal with Berries" and "Yogurt"
            5. "2 coronas" -> ONE item: "Corona Beer (2 bottles)" with calories/protein/carbs/fats multiplied by 2
            6. "3 cups of rice" -> ONE item: "Rice (3 cups)" with calories/protein/carbs/fats multiplied by 3
            7. "1/2 avocado" -> ONE item: "Avocado (1/2)" with calories/protein/carbs/fats multiplied by 0.5
            
            Additional Guidelines:
            - normalized_title should be clear and presentable, include quantity if specified
            - meal_type should be one of: breakfast, lunch, dinner, snack, or drink
            - All nutritional values should be numbers and account for quantities
            - confidence_score should be between 0 and 1 for each item
            - Include notes if there are any uncertainties or important details to mention
            - Calculate total_nutrition by summing up the nutritional values of all items
            - In notes, mention if the food aligns with our guidelines (encourage good choices, gently note areas for improvement)
            - Tone: Be realistic and encouraging, not overly enthusiastic. Use matter-of-fact but warm language
            - Focus on the positive aspects of food choices while gently noting areas for improvement
            - Maintain positive associations with food and eating - avoid judgmental language
            - Keep notes concise and actionable
            - ALWAYS account for quantities in your nutritional calculations
            """

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable nutrition expert providing realistic, encouraging diet advice via SMS. Be helpful and supportive while maintaining a balanced, non-judgmental tone. Focus on the positive aspects of food choices while gently noting areas for improvement. Avoid overly enthusiastic language - be matter-of-fact but warm. Keep responses brief, mobile-friendly, and actionable while maintaining positive associations with food and eating."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500  # Reduced from 1000 to encourage brevity
            )

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("No response content received from OpenAI")

            # Parse the response
            analysis = json.loads(response.choices[0].message.content)
            
            # Validate the response structure
            required_fields = ["meal_type", "items", "total_nutrition"]
            nutrition_fields = ["calories", "protein", "carbs", "fats"]
            
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            if not isinstance(analysis["items"], list) or len(analysis["items"]) == 0:
                raise ValueError("Items must be a non-empty list")
            
            # Validate each item
            for item in analysis["items"]:
                if "normalized_title" not in item:
                    raise ValueError("Each item must have a normalized_title")
                if "nutrition" not in item:
                    raise ValueError("Each item must have nutrition information")
                if "confidence_score" not in item:
                    raise ValueError("Each item must have a confidence_score")
                
                for field in nutrition_fields:
                    if field not in item["nutrition"]:
                        raise ValueError(f"Each item must have {field} in nutrition")
                    if not isinstance(item["nutrition"][field], (int, float)):
                        raise ValueError(f"Nutrition field {field} must be a number")
                
                if not isinstance(item["confidence_score"], (int, float)) or not 0 <= item["confidence_score"] <= 1:
                    raise ValueError("Confidence score must be a number between 0 and 1")
            
            # Validate total nutrition
            for field in nutrition_fields:
                if field not in analysis["total_nutrition"]:
                    raise ValueError(f"Missing {field} in total_nutrition")
                if not isinstance(analysis["total_nutrition"][field], (int, float)):
                    raise ValueError(f"Total nutrition field {field} must be a number")
            
            if analysis["meal_type"] not in ["breakfast", "lunch", "dinner", "snack", "drink"]:
                raise ValueError("Invalid meal type")
            
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing food entry: {str(e)}")
            raise

    async def analyze_diet_question(self, question: str, user_data: Dict[str, Any], food_logs_summary: Dict[str, Any]) -> str:
        """
        Analyze a user's question about their diet and provide a response, taking into account their food log history.
        """
        try:
            # Format the food logs summary into a readable format
            daily_logs_text = []
            for date, data in sorted(food_logs_summary["daily_logs"].items(), reverse=True):
                daily_logs_text.append(f"\n{date}:")
                for item in data["items"]:
                    daily_logs_text.append(f"- {item['meal_type'].title()}: {item['title']}")
                    daily_logs_text.append(f"  Calories: {item['calories']:.0f}, Protein: {item['protein']:.1f}g, Carbs: {item['carbs']:.1f}g, Fats: {item['fats']:.1f}g")
                daily_logs_text.append(f"Daily Total: {data['calories']:.0f} calories, {data['protein']:.1f}g protein, {data['carbs']:.1f}g carbs, {data['fats']:.1f}g fats")
            
            # Format meal type distribution
            meal_distribution = "\n".join(f"- {meal_type}: {count} entries" for meal_type, count in food_logs_summary["meal_type_distribution"].items())
            
            prompt = f"""
            You are a nutrition expert providing personalized diet advice via SMS. Your responses should be:
            1. Concise and to the point (aim for 2-3 short paragraphs max)
            2. Easy to read on mobile (use emojis sparingly, avoid complex formatting)
            3. Actionable and specific
            4. Friendly and encouraging in tone
            5. Aligned with our product's core principles

            PRODUCT GUIDELINES - BASE ALL ADVICE ON THESE PRINCIPLES:
            
            FOODS TO EAT (Encourage these):
            • Meats, poultry & fish: steak, ground beef, ground bison, ground turkey, eggs, chicken breast, turkey breast, pork tenderloin, elk, venison, salmon, shrimp, cod, tilapia, tuna
            • Dairy: plain/greek yogurt, cottage cheese, milk, cheese
            • Grains: oatmeal, white rice, quinoa, popcorn
            • Vegetables: white potatoes, sweet potatoes, beets, spinach, broccoli, asparagus, tomatoes, peppers, mushrooms, cucumbers, zucchini, green beans, leafy salad greens
            • Fruits: apples, berries, bananas, oranges, grapes, watermelon, peaches, pears
            • Nuts & Seeds: walnuts, almonds, brazil nuts, macadamia nuts, flax seeds, sunflower seeds, chia seeds
            • Beans & Legumes: pinto beans, black beans, kidney beans, chickpeas, lentils
            • Oils/Fats: butter, ghee, olive oil, coconut oil, avocado oil, flaxseed oil
            
            FOODS TO LIMIT/AVOID (Discourage these):
            • Deep-fried foods
            • Added Sugars
            • Alcohol
            
            GENERAL PRINCIPLES (Incorporate these in advice):
            • Drink at least half your bodyweight [in ounces] of water daily
            • Consume 16-24oz of water first thing in the morning, every morning, to get a "jump start" on your hydration
            • Eliminate all beverages besides water, coffee/tea & protein shakes
            • Eat protein with every meal
            • Eat 1-3 servings fruit & 2-4 servings vegetables daily
            • Eat until satisfied, not "full"
            • Chew your food thoroughly
            • Spread your calories out over 3+ meals each day
            • Do all your food shopping after eating [never food shop when hungry]
            • Always Plan Ahead!

            User Profile:
            - Target Calories: {user_data.get('target_calories')}
            - Target Protein: {user_data.get('target_protein')}g
            - Target Carbs: {user_data.get('target_carbs')}g
            - Target Fats: {user_data.get('target_fats')}g
            
            Recent Food Log Summary (Last {food_logs_summary['days_analyzed']} days):
            Average Daily Intake:
            - Calories: {food_logs_summary['averages']['calories']:.0f}
            - Protein: {food_logs_summary['averages']['protein']:.1f}g
            - Carbs: {food_logs_summary['averages']['carbs']:.1f}g
            - Fats: {food_logs_summary['averages']['fats']:.1f}g
            
            Meal Type Distribution:
            {meal_distribution}
            
            Detailed Food Logs:
            {''.join(daily_logs_text)}
            
            User Question: "{question}"
            
            Guidelines for your response:
            1. Start with a direct answer to their question
            2. Include 1-2 key insights from their food logs
            3. End with 1-2 specific, actionable suggestions that align with our guidelines
            4. Keep it under 160 characters per line
            5. Use simple language and avoid jargon
            6. If using numbers, round to whole numbers where possible
            7. Use line breaks (\\n) to separate key points
            8. Avoid complex formatting, tables, or lists
            9. Always encourage foods from our "FOODS TO EAT" list
            10. Gently suggest alternatives for foods from our "LIMIT/AVOID" list
            11. Incorporate our general principles when relevant (hydration, protein, meal timing, etc.)
            12. Tone: Be realistic and encouraging, not overly enthusiastic. Use matter-of-fact but warm language
            13. Focus on the positive aspects of food choices while gently noting areas for improvement
            14. Maintain positive associations with food and eating - avoid judgmental language
            15. Be supportive without being pushy or overly optimistic
            
            Example response format:
            "Your current average of 1800 cal/day looks good for your goals.

            I notice your protein intake is around 80g - adding Greek yogurt to breakfast or a protein shake as a snack could help reach your target.

            Your lunch salads are a great foundation. Consider adding more protein like chicken or tofu to make them more satisfying."
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable nutrition expert providing realistic, encouraging diet advice via SMS. Be helpful and supportive while maintaining a balanced, non-judgmental tone. Focus on the positive aspects of food choices while gently noting areas for improvement. Avoid overly enthusiastic language - be matter-of-fact but warm. Keep responses brief, mobile-friendly, and actionable while maintaining positive associations with food and eating."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500  # Reduced from 1000 to encourage brevity
            )

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("No response content received from OpenAI")

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error analyzing diet question: {str(e)}")
            raise 