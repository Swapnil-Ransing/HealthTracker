"""
Recommendations module for generating personalized calorie and macro targets.
Supabase-compatible version (no SQLite usage).
"""

from typing import Dict, Optional
from db.database import get_user, get_settings, supabase

from utils.calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_calories_for_weight_loss,
    calculate_macronutrient_targets,
    calculate_exercise_calories
)

import os
from dotenv import load_dotenv

load_dotenv()

# GPT Client
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
except:
    client = None


# ==================== GPT RECOMMENDATIONS ====================

def generate_gpt_recommendations(user_id: int) -> Optional[Dict]:
    if not client:
        return None

    user = get_user(user_id)
    if not user:
        return None

    settings = get_settings(user_id)

    age = user['age']
    gender = user['gender']
    height = user['height']
    current_weight = user['current_weight']
    target_weight = user['target_weight']

    weight_to_lose = current_weight - target_weight

    activity_level = settings.get('activity_level', 'moderate')
    diet_preference = settings.get('diet_preference', 'balanced')

    prompt = f"""
You are a fitness expert.

User:
Age: {age}
Gender: {gender}
Height: {height}
Weight: {current_weight}
Target: {target_weight}
Activity: {activity_level}
Diet: {diet_preference}

Return JSON:
{{
"daily_calories": number,
"protein_grams": number,
"carbs_grams": number,
"fat_grams": number,
"calorie_deficit": number,
"weekly_weight_loss": number,
"diet_type": string,
"reasoning": string,
"tips": [string]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return only JSON"},
                {"role": "user", "content": prompt}
            ]
        )

        import json
        return json.loads(response.choices[0].message.content)

    except:
        return None


# ==================== CALCULATED RECOMMENDATIONS ====================

def generate_calculated_recommendations(user_id: int) -> Dict:
    user = get_user(user_id)
    if not user:
        return None

    settings = get_settings(user_id)

    activity_level = settings.get('activity_level', 'moderate')
    diet_preference = settings.get('diet_preference', 'balanced')
    target_loss_per_week = settings.get('target_loss_per_week', 0.5)

    bmr = calculate_bmr(
        user['gender'],
        user['age'],
        user['height'],
        user['current_weight']
    )

    tdee = calculate_tdee(bmr, activity_level)

    exercise_calories = calculate_exercise_calories(tdee, bmr)

    loss_plan = calculate_calories_for_weight_loss(tdee, target_loss_per_week)

    macros = calculate_macronutrient_targets(
        loss_plan['daily_calorie_intake'],
        diet_preference
    )

    weight_to_lose = user['current_weight'] - user['target_weight']

    return {
        'daily_calories': round(loss_plan['daily_calorie_intake']),
        'protein_grams': macros['protein_g'],
        'carbs_grams': macros['carbs_g'],
        'fat_grams': macros['fat_g'],
        'fiber_grams': macros['fiber_g'],
        'calorie_deficit': round(loss_plan['daily_deficit']),
        'exercise_calories': round(exercise_calories),
        'weekly_weight_loss': target_loss_per_week,
        'diet_type': diet_preference,
        'bmr': round(bmr),
        'tdee': round(tdee),
        'tips': [
            f"Protein: {macros['protein_g']}g daily",
            f"Fiber: {macros['fiber_g']}g daily",
            "Stay consistent with logging",
            "Hydration is key"
        ]
    }


# ==================== SAVE RECOMMENDATIONS ====================

def save_recommendations(user_id: int, rec: Dict) -> bool:
    try:
        supabase.table("settings").upsert({
            "user_id": user_id,
            "recommended_daily_calories": rec.get('daily_calories', 0),
            "recommended_protein": rec.get('protein_grams', 0),
            "recommended_carbs": rec.get('carbs_grams', 0),
            "recommended_fat": rec.get('fat_grams', 0),
            "exercise_calories_target": rec.get('exercise_calories', 0),
            "diet_preference": rec.get('diet_type', 'balanced'),
            "use_recommendations": True
        }).execute()

        return True

    except Exception as e:
        print("Error saving recommendations:", e)
        return False


# ==================== CUSTOM GOALS ====================

def save_custom_recommendations(user_id: int, goals: Dict) -> bool:
    try:
        supabase.table("settings").upsert({
            "user_id": user_id,
            "custom_calorie_goal": goals.get('daily_calories', 0),
            "custom_protein_goal": goals.get('protein_grams', 0),
            "custom_carbs_goal": goals.get('carbs_grams', 0),
            "custom_fat_goal": goals.get('fat_grams', 0),
            "calorie_deficit_constant": goals.get('calorie_deficit', 500),
            "use_recommendations": False
        }).execute()

        return True

    except Exception as e:
        print("Error saving custom goals:", e)
        return False


# ==================== GET ACTIVE ====================

def get_active_recommendations(user_id: int) -> Dict:
    settings = get_settings(user_id)
    if not settings:
        return None

    if settings.get('use_recommendations', True):
        return {
            'daily_calories': settings.get('recommended_daily_calories', 0),
            'protein_grams': settings.get('recommended_protein', 0),
            'carbs_grams': settings.get('recommended_carbs', 0),
            'fat_grams': settings.get('recommended_fat', 0),
            'calorie_deficit': settings.get('calorie_deficit_constant', 500),
            'source': 'calculated'
        }
    else:
        return {
            'daily_calories': settings.get('custom_calorie_goal', 0),
            'protein_grams': settings.get('custom_protein_goal', 0),
            'carbs_grams': settings.get('custom_carbs_goal', 0),
            'fat_grams': settings.get('custom_fat_goal', 0),
            'calorie_deficit': settings.get('calorie_deficit_constant', 500),
            'source': 'custom'
        }


# ==================== UPDATE PREFERENCES ====================

def update_user_profile_preferences(user_id: int,
                                    activity_level: str = None,
                                    diet_preference: str = None,
                                    target_loss_per_week: float = None) -> bool:
    try:
        update_data = {}

        if activity_level:
            update_data["activity_level"] = activity_level

        if diet_preference:
            update_data["diet_preference"] = diet_preference

        if target_loss_per_week is not None:
            update_data["target_loss_per_week"] = target_loss_per_week

        # Settings record already exists for every user, so only update
        supabase.table("settings").update(update_data).eq("user_id", user_id).execute()

        return True

    except Exception as e:
        print("Error updating preferences:", e)
        return False


if __name__ == "__main__":
    print("✅ Recommendations module ready (Supabase)")