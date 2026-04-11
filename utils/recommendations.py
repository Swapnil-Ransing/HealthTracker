"""
Recommendations module for generating personalized calorie and macro targets.
Uses both calculation-based and GPT-based approaches.
"""

import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from typing import Dict, Optional
from database import get_user, get_settings, get_db_connection
from calculations import (
    calculate_bmr, calculate_tdee,
    calculate_calories_for_weight_loss,
    calculate_macronutrient_targets,
    calculate_exercise_calories
)
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
except:
    client = None


def generate_gpt_recommendations(user_id: int) -> Optional[Dict]:
    """
    Generate personalized recommendations using GPT based on user profile.
    
    Args:
        user_id: User ID
    
    Returns:
        {
            'daily_calories': float,
            'protein_grams': float,
            'carbs_grams': float,
            'fat_grams': float,
            'calorie_deficit': float,
            'weekly_weight_loss': float,
            'diet_type': str,
            'reasoning': str,
            'tips': list
        }
    """
    # Ensure database is migrated with all required columns
    from database import migrate_db
    try:
        migrate_db()
    except:
        pass  # Continue even if migration fails
    
    if not client:
        return None
    
    user = get_user(user_id)
    if not user:
        return None
    
    # Prepare user profile summary
    age = user['age']
    gender = user['gender']
    height = user['height']
    current_weight = user['current_weight']
    target_weight = user['target_weight']
    weight_to_lose = current_weight - target_weight
    
    # Get settings
    settings = get_settings(user_id)
    activity_level = settings.get('activity_level', 'moderate') if settings else 'moderate'
    diet_preference = settings.get('diet_preference', 'balanced') if settings else 'balanced'
    
    # Create detailed prompt
    prompt = f"""You are a fitness and nutrition expert. Based on the following user profile, generate personalized calorie and macro recommendations:

USER PROFILE:
- Name: {user['name']}
- Age: {age} years old
- Gender: {gender}
- Height: {height} cm
- Current Weight: {current_weight} kg
- Target Weight: {target_weight} kg
- Weight to lose: {weight_to_lose} kg
- Activity Level: {activity_level} (sedentary/light/moderate/very_active/extremely_active)
- Diet Preference: {diet_preference} (balanced/high_protein/low_carb/vegetarian)

Please provide recommendations in JSON format with these fields:
{{
    "daily_calories": <recommended daily calorie intake (number)>,
    "protein_grams": <daily protein in grams (number)>,
    "carbs_grams": <daily carbs in grams (number)>,
    "fat_grams": <daily fat in grams (number)>,
    "calorie_deficit": <daily deficit constant in kcal (number)>,
    "weekly_weight_loss": <estimated kg per week (number)>,
    "diet_type": "<suggested diet type>",
    "reasoning": "<brief explanation of recommendations>",
    "tips": [<list of 3-4 actionable tips for this user>]
}}

Consider:
- BMR required for maintenance
- Activity level multiplier
- Weight loss timeline ({weight_to_lose}kg target)
- Diet preference alignment
- Realistic and sustainable targets

Respond ONLY with valid JSON, no markdown or extra text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fitness and nutrition expert. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        import json
        response_text = response.choices[0].message.content.strip()
        recommendations = json.loads(response_text)
        
        return recommendations
    
    except Exception as e:
        return None


def generate_calculated_recommendations(user_id: int) -> Dict:
    """
    Generate recommendations using calculation-based approach (no GPT).
    
    Args:
        user_id: User ID
    
    Returns:
        Recommendations dict
    """
    # Ensure database is migrated with all required columns
    from database import migrate_db
    try:
        migrate_db()
    except:
        pass  # Continue even if migration fails
    
    user = get_user(user_id)
    if not user:
        return None
    
    settings = get_settings(user_id)
    activity_level = settings.get('activity_level', 'moderate') if settings else 'moderate'
    diet_preference = settings.get('diet_preference', 'balanced') if settings else 'balanced'
    target_loss_per_week = settings.get('target_loss_per_week', 0.5) if settings else 0.5
    
    # Calculate BMR and TDEE
    bmr = calculate_bmr(user['gender'], user['age'], user['height'], user['current_weight'])
    tdee = calculate_tdee(bmr, activity_level)
    
    # Calculate exercise calories (TDEE - BMR)
    exercise_calories = calculate_exercise_calories(tdee, bmr)
    
    # Calculate weight loss plan
    loss_plan = calculate_calories_for_weight_loss(tdee, target_loss_per_week)
    
    # Get macro targets
    macro_targets = calculate_macronutrient_targets(
        loss_plan['daily_calorie_intake'],
        diet_preference
    )
    
    # Weight loss projection
    weight_to_lose = user['current_weight'] - user['target_weight']
    weeks_to_goal = weight_to_lose / target_loss_per_week if target_loss_per_week > 0 else 0
    
    return {
        'daily_calories': round(loss_plan['daily_calorie_intake'], 0),
        'protein_grams': macro_targets['protein_g'],
        'carbs_grams': macro_targets['carbs_g'],
        'fat_grams': macro_targets['fat_g'],
        'fiber_grams': macro_targets['fiber_g'],
        'calorie_deficit': round(loss_plan['daily_deficit'], 0),
        'exercise_calories': round(exercise_calories, 0),
        'weekly_weight_loss': target_loss_per_week,
        'diet_type': diet_preference,
        'reasoning': f"Based on {activity_level} activity level and {diet_preference} diet preference",
        'tips': [
            f"Aim for {macro_targets['protein_g']}g protein and {macro_targets['fiber_g']}g fiber daily for satiety",
            f"Log meals consistently to track {loss_plan['daily_calorie_intake']} kcal target",
            f"You can lose ~{weight_to_lose}kg in approximately {weeks_to_goal:.0f} weeks at this pace",
            "Drink plenty of water and eat fiber-rich foods for optimal digestion and results"
        ],
        'bmr': round(bmr, 0),
        'tdee': round(tdee, 0)
    }


def save_recommendations(user_id: int, recommendations: Dict, use_gpt: bool = True) -> bool:
    """
    Save recommendations to database.
    
    Args:
        user_id: User ID
        recommendations: Recommendations dict
        use_gpt: Whether recommendations came from GPT
    
    Returns:
        Success boolean
    """
    # Ensure database is migrated with all required columns
    from database import migrate_db
    try:
        migrate_db()
    except:
        pass  # Continue even if migration fails
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure settings row exists for user
        cursor.execute(
            "INSERT OR IGNORE INTO settings (user_id) VALUES (?)",
            (user_id,)
        )
        
        cursor.execute("""
            UPDATE settings
            SET recommended_daily_calories = ?,
                recommended_protein = ?,
                recommended_carbs = ?,
                recommended_fat = ?,
                exercise_calories_target = ?,
                diet_preference = ?,
                use_recommendations = 1,
                custom_calorie_goal = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (
            recommendations.get('daily_calories', 0),
            recommendations.get('protein_grams', 0),
            recommendations.get('carbs_grams', 0),
            recommendations.get('fat_grams', 0),
            recommendations.get('exercise_calories', 0),
            recommendations.get('diet_type', 'balanced'),
            user_id
        ))
        
        conn.commit()
        return True
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()


def save_custom_recommendations(user_id: int, custom_goals: Dict) -> bool:
    """
    Save user's custom override recommendations.
    
    Args:
        user_id: User ID
        custom_goals: {
            'daily_calories': float,
            'protein_grams': float,
            'carbs_grams': float,
            'fat_grams': float,
            'calorie_deficit': float
        }
    
    Returns:
        Success boolean
    """
    # Ensure database is migrated with all required columns
    from database import migrate_db
    try:
        migrate_db()
    except:
        pass  # Continue even if migration fails
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure settings row exists for user
        cursor.execute(
            "INSERT OR IGNORE INTO settings (user_id) VALUES (?)",
            (user_id,)
        )
        
        cursor.execute("""
            UPDATE settings
            SET custom_calorie_goal = ?,
                custom_protein_goal = ?,
                custom_carbs_goal = ?,
                custom_fat_goal = ?,
                calorie_deficit_constant = ?,
                use_recommendations = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (
            custom_goals.get('daily_calories', 0),
            custom_goals.get('protein_grams', 0),
            custom_goals.get('carbs_grams', 0),
            custom_goals.get('fat_grams', 0),
            custom_goals.get('calorie_deficit', 500),
            user_id
        ))
        
        conn.commit()
        return True
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()


def get_active_recommendations(user_id: int) -> Dict:
    """
    Get active recommendations (either calculated or custom).
    
    Args:
        user_id: User ID
    
    Returns:
        Active recommendations dict
    """
    # Ensure database is migrated with all required columns
    from database import migrate_db
    try:
        migrate_db()
    except:
        pass  # Continue even if migration fails
    
    settings = get_settings(user_id)
    
    if not settings:
        return None
    
    if settings.get('use_recommendations', 1):
        # Using calculated recommendations
        return {
            'daily_calories': settings.get('recommended_daily_calories', 0),
            'protein_grams': settings.get('recommended_protein', 0),
            'carbs_grams': settings.get('recommended_carbs', 0),
            'fat_grams': settings.get('recommended_fat', 0),
            'calorie_deficit': settings.get('calorie_deficit_constant', 500),
            'source': 'calculated'
        }
    else:
        # Using custom goals
        return {
            'daily_calories': settings.get('custom_calorie_goal', 0),
            'protein_grams': settings.get('custom_protein_goal', 0),
            'carbs_grams': settings.get('custom_carbs_goal', 0),
            'fat_grams': settings.get('custom_fat_goal', 0),
            'calorie_deficit': settings.get('calorie_deficit_constant', 500),
            'source': 'custom'
        }


def update_user_profile_preferences(user_id: int, activity_level: str = None,
                                    diet_preference: str = None,
                                    target_loss_per_week: float = None) -> bool:
    """
    Update user's profile preferences for recommendations.
    
    Args:
        user_id: User ID
        activity_level: Activity level for calculations
        diet_preference: Diet type preference
        target_loss_per_week: Target weight loss per week
    
    Returns:
        Success boolean
    """
    # Ensure database is migrated with all required columns
    from database import migrate_db
    try:
        migrate_db()
    except:
        pass  # Continue even if migration fails
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure settings row exists for user
        cursor.execute(
            "INSERT OR IGNORE INTO settings (user_id) VALUES (?)",
            (user_id,)
        )
        
        if activity_level:
            cursor.execute(
                "UPDATE settings SET activity_level = ? WHERE user_id = ?",
                (activity_level, user_id)
            )
        
        if diet_preference:
            cursor.execute(
                "UPDATE settings SET diet_preference = ? WHERE user_id = ?",
                (diet_preference, user_id)
            )
        
        if target_loss_per_week is not None:
            cursor.execute(
                "UPDATE settings SET target_loss_per_week = ? WHERE user_id = ?",
                (target_loss_per_week, user_id)
            )
        
        conn.commit()
        return True
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("Recommendations module loaded successfully!")
