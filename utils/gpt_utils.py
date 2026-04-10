"""
GPT Integration module for calorie calculation from meal descriptions.
Uses OpenAI API to parse natural language meal descriptions and extract nutrition data.
"""

import os
import json
import re
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, APIError, AuthenticationError

load_dotenv()

# Configure OpenAI API
api_key = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=api_key) if api_key else None
MODEL = "gpt-3.5-turbo"

# Meal cache to avoid repeated API calls for same meals
_meal_cache = {}


def calculate_nutrition_from_meal(meal_description: str, retry_on_error: bool = True) -> Tuple[bool, Optional[Dict]]:
    """
    Parse a meal description using GPT and return nutrition information.
    
    Args:
        meal_description: Natural language description of meal (e.g., "2 eggs, 1 toast with butter")
        retry_on_error: Whether to retry on API failure
    
    Returns:
        (success: bool, nutrition_data: dict or None)
        
    nutrition_data format:
    {
        'meal_description': str,
        'calories': float,
        'protein': float,  # grams
        'carbs': float,    # grams
        'fat': float,      # grams
        'fiber': float,    # grams
        'assumptions': str  # any assumptions made by GPT
    }
    """
    
    if not meal_description or len(meal_description.strip()) == 0:
        return (False, None)
    
    if not client:
        print("❌ OpenAI API client not initialized. Check your API key.")
        return (False, None)
    
    # Normalize meal description
    meal_key = meal_description.lower().strip()
    
    # Check cache first
    if meal_key in _meal_cache:
        # Silently return cached result
        return (True, _meal_cache[meal_key])
    
    # Create GPT prompt
    prompt = f"""Analyze this meal description and provide nutritional information in JSON format.

Meal: {meal_description}

Please respond ONLY with a JSON object (no markdown, no extra text) with these fields:
- calories: total calories in kcal (float)
- protein: grams of protein (float)
- carbs: grams of carbohydrates (float)
- fat: grams of fat (float)
- fiber: grams of fiber (float)
- assumptions: brief description of assumptions you made (string)

Example response:
{{"calories": 350.0, "protein": 20.0, "carbs": 40.0, "fat": 12.0, "fiber": 2.5, "assumptions": "Assumed medium-sized portions, toast with 1 tbsp butter"}}

Make realistic estimates based on typical portion sizes."""

    try:
        # Call OpenAI API (new 1.0.0+ syntax)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutritionist AI that analyzes meal descriptions and estimates their nutritional content. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=200
        )
        
        # Extract response
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            nutrition_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON if wrapped in markdown code blocks
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                nutrition_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from GPT response")
        
        # Validate response
        required_fields = ['calories', 'protein', 'carbs', 'fat', 'fiber']
        for field in required_fields:
            if field not in nutrition_data:
                nutrition_data[field] = 0.0
            else:
                nutrition_data[field] = float(nutrition_data[field])
        
        # Add meal description
        nutrition_data['meal_description'] = meal_description
        
        # Cache the result
        _meal_cache[meal_key] = nutrition_data
        
        return (True, nutrition_data)
    
    except RateLimitError:
        # Silently handle rate limit
        return (False, None)
    
    except AuthenticationError:
        # Silently handle auth error
        return (False, None)
    
    except APIError as e:
        # Silently handle API error
        if retry_on_error:
            return calculate_nutrition_from_meal(meal_description, retry_on_error=False)
        return (False, None)
    
    except Exception as e:
        # Silently handle other errors
        return (False, None)


def calculate_nutrition_for_multiple_meals(meals: list) -> Dict:
    """
    Calculate nutrition for multiple meals and return aggregated totals.
    
    Args:
        meals: List of meal descriptions
    
    Returns:
        {
            'total_calories': float,
            'total_protein': float,
            'total_carbs': float,
            'total_fat': float,
            'total_fiber': float,
            'meal_details': [list of individual meal data],
            'success_count': int,
            'error_count': int
        }
    """
    
    if not meals:
        return {
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'total_fiber': 0,
            'meal_details': [],
            'success_count': 0,
            'error_count': 0
        }
    
    totals = {
        'total_calories': 0,
        'total_protein': 0,
        'total_carbs': 0,
        'total_fat': 0,
        'total_fiber': 0,
        'meal_details': [],
        'success_count': 0,
        'error_count': 0
    }
    
    for meal in meals:
        success, nutrition = calculate_nutrition_from_meal(meal)
        
        if success and nutrition:
            totals['total_calories'] += nutrition['calories']
            totals['total_protein'] += nutrition['protein']
            totals['total_carbs'] += nutrition['carbs']
            totals['total_fat'] += nutrition['fat']
            totals['total_fiber'] += nutrition['fiber']
            totals['meal_details'].append(nutrition)
            totals['success_count'] += 1
        else:
            totals['error_count'] += 1
    
    return totals


def clear_cache():
    """Clear the meal cache (useful for testing)."""
    global _meal_cache
    _meal_cache = {}


def get_cache_stats():
    """Get statistics about the meal cache."""
    return {
        'cached_meals': len(_meal_cache),
        'meals': list(_meal_cache.keys())
    }


def validate_api_key() -> bool:
    """Validate that OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    return bool(api_key and api_key.startswith("sk-"))


if __name__ == "__main__":
    # Test the GPT module
    print("GPT Utils module loaded successfully!")
    if validate_api_key():
        print("✅ OpenAI API key is configured")
        if client:
            print("✅ OpenAI client initialized successfully")
        else:
            print("❌ OpenAI client failed to initialize")
    else:
        print("❌ OpenAI API key is not configured")
