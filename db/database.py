"""
Database module for HealthTracker - Supabase version
"""

from supabase import create_client
import os
import streamlit as st
from datetime import datetime
from typing import Optional, List, Dict
import hashlib
import secrets

# ==================== SUPABASE SETUP ====================

def get_secret(key):
    try:
        return st.secrets[key]
    except:
        return os.getenv(key)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ==================== PASSWORD ====================

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, pwd_hash = password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == pwd_hash
    except:
        return False

# ==================== USER ====================
import time

def execute_with_retry(query_fn, retries=3, delay=0.5):
    for attempt in range(retries):
        try:
            return query_fn()
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(delay * (attempt + 1))


def create_user(username, password, name, family_id=None,
                gender=None, age=None, height=None,
                current_weight=None, target_weight=None):

    try:
        password_hash = hash_password(password)

        res = supabase.table("users").insert({
            "username": username,
            "password_hash": password_hash,
            "name": name,
            "family_id": family_id,
            "gender": gender,
            "age": age,
            "height": height,
            "current_weight": current_weight,
            "target_weight": target_weight
        }).execute()

        user_id = res.data[0]["user_id"]

        # create default settings
        supabase.table("settings").insert({
            "user_id": user_id
        }).execute()

        return user_id

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

@st.cache_data(ttl=600) # Cache for 10 minutes
def get_user(user_id: int):
    def query():
        return supabase.table("users") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()

    res = execute_with_retry(query)

    return res.data[0] if res.data else None


def get_user_by_username(username: str):
    def query():
        return supabase.table("users") \
            .select("*") \
            .eq("username", username) \
            .execute()
    res = execute_with_retry(query)
    return res.data[0] if res.data else None


def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if user and verify_password(password, user['password_hash']):
        return user['user_id']
    return None


def user_exists(username: str):
    return get_user_by_username(username) is not None
    
def update_user_profile(user_id: int, **kwargs):
    allowed_fields = ['name', 'gender', 'age', 'height', 'current_weight', 'target_weight']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return True
    
    try:
        supabase.table("users").update(updates).eq("user_id", user_id).execute()
        # CLEAR THE CACHE so get_user() fetches fresh data next time
        get_user.clear(user_id) 
        return True
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return False

# ==================== FAMILY ====================

def generate_family_code():
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(6))


def create_family(family_name: str, created_by: int):
    try:
        code = generate_family_code()

        res = supabase.table("families").insert({
            "family_name": family_name,
            "family_code": code,
            "created_by": created_by
        }).execute()

        return res.data[0]["family_id"]
    except Exception as e:
        print(e)
        return None

def get_family(family_id: int):
    """Get family by ID"""
    try:
        response = supabase.table("families").select("*").eq("family_id", family_id).execute()

        if response.data:
            return response.data[0]

        return None

    except Exception as e:
        print(f"❌ Error fetching family: {e}")
        return None

def get_family_by_code(code: str):
    res = supabase.table("families").select("*").eq("family_code", code).execute()
    return res.data[0] if res.data else None


def get_family_members(family_id: int):
    res = supabase.table("users").select("*").eq("family_id", family_id).execute()
    return res.data


def add_user_to_family(user_id: int, family_id: int):
    supabase.table("users").update({"family_id": family_id}).eq("user_id", user_id).execute()
    return True

# ==================== MEALS ====================

def log_meal(user_id, date, meal_type, meal_description,
             calories=None, protein=None, carbs=None,
             fat=None, fiber=None, gpt_raw_response=None):

    try:
        res = supabase.table("nutrition_log").insert({
            "user_id": user_id,
            "date": date,
            "meal_type": meal_type,
            "meal_description": meal_description,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "fiber": fiber,
            "gpt_raw_response": gpt_raw_response
        }).execute()

        return res.data[0]["id"]

    except Exception as e:
        print(e)
        return None


def get_meals_by_date(user_id, date):
    res = supabase.table("nutrition_log") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("date", date) \
        .execute()

    return res.data

def delete_meal(meal_id: int) -> bool:
    """
    Delete a meal by ID from Supabase.
    """
    try:
        supabase.table("nutrition_log") \
            .delete() \
            .eq("id", meal_id) \
            .execute()
        return True
    except Exception as e:
        print(f"❌ Error deleting meal: {e}")
        return False

def update_meal(meal_id: int, **kwargs) -> bool:
    """
    Update a meal's nutritional information in Supabase.
    
    Args:
        meal_id: The meal ID to update
        **kwargs: Fields to update (calories, protein, carbs, fat, fiber, etc.)
    
    Returns:
        True if successful, False otherwise
    """
    allowed_fields = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'meal_description', 'gpt_raw_response']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return True
    
    try:
        supabase.table("nutrition_log").update(updates).eq("id", meal_id).execute()
        return True
    except Exception as e:
        print(f"❌ Error updating meal: {e}")
        return False

def get_meals_by_date_range(user_id, start_date, end_date):
    try:
        res = supabase.table("nutrition_log") \
            .select("*") \
            .eq("user_id", user_id) \
            .gte("date", start_date) \
            .lte("date", end_date) \
            .order("date") \
            .execute()

        return res.data
    except Exception as e:
        print(f"❌ Error fetching meals range: {e}")
        return [] 
    
# ==================== WATER ====================

def log_water(user_id, date, water_liters, time=None):
    res = supabase.table("water_log").insert({
        "user_id": user_id,
        "date": date,
        "water_intake_liters": water_liters,
        "time": time
    }).execute()

    return res.data[0]["id"]


def get_total_water_by_date(user_id, date):
    res = supabase.table("water_log") \
        .select("water_intake_liters") \
        .eq("user_id", user_id) \
        .eq("date", date) \
        .execute()

    return sum([x["water_intake_liters"] or 0 for x in res.data])

def get_water_log_by_date(user_id, date):
    try:
        res = supabase.table("water_log") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("date", date) \
            .execute()

        return res.data
    except Exception as e:
        print(f"❌ Error fetching water log: {e}")
        return []

def delete_water_log(water_id: int) -> bool:
    """
    Delete a water log entry by ID from Supabase.
    
    Args:
        water_id: The water log ID to delete
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase.table("water_log") \
            .delete() \
            .eq("id", water_id) \
            .execute()
        return True
    except Exception as e:
        print(f"❌ Error deleting water log: {e}")
        return False

# ==================== DAILY SUMMARY ====================

# database.py

def save_daily_summary(user_id, date, **kwargs):
    """
    Optimized to update only provided fields (like water or calories) 
    without overwriting existing data for that day.
    """
    try:
        # Get existing record to prevent overwriting other metrics with 0
        existing = supabase.table("daily_summary") \
            .select("*").eq("user_id", user_id).eq("date", date).execute()
        
        data = existing.data[0] if existing.data else {"user_id": user_id, "date": date}
        
        # Merge new data (e.g., water_intake_liters) into the record
        for key, value in kwargs.items():
            data[key] = value

        supabase.table("daily_summary").upsert(data).execute()
        # CLEAR THE ANALYTICS CACHE
        get_daily_summaries_range.clear(user_id)
        return True
    except Exception as e:
        print(f"❌ Sync Error: {e}")
        return False

def update_daily_summary_weight(user_id, date, weight):
    try:
        supabase.table("daily_summary") \
            .update({
                "weight": weight
            }) \
            .eq("user_id", user_id) \
            .eq("date", date) \
            .execute()
        return True
    except Exception as e:
        print(f"❌ Error updating weight: {e}")
        return False
    
def update_daily_summary_cheat_day(user_id, date, is_cheat_day):
    try:
        supabase.table("daily_summary") \
            .update({
                "is_cheat_day": is_cheat_day
            }) \
            .eq("user_id", user_id) \
            .eq("date", date) \
            .execute()
        return True
    except Exception as e:
        print(f"❌ Error updating cheat day: {e}")
        return False

def get_daily_summary(user_id, date):
    res = supabase.table("daily_summary") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("date", date) \
        .execute()

    if not res.data:
        return {}

    data = res.data[0]

    # ✅ Normalize all numeric fields
    numeric_fields = [
        "calories_consumed", "protein", "carbs", "fat", "fiber",
        "calories_walk", "calories_gym", "calories_burned",
        "calorie_deficit", "water_intake_liters", "weight"
    ]

    for field in numeric_fields:
        if data.get(field) is None:
            data[field] = 0.0

    return data

def update_daily_summary_activity(user_id, date, activity_type,
                                  duration_or_distance,
                                  pace_or_intensity,
                                  calories_burned):
    try:
        if activity_type == "gym":
            field = "calories_gym"
        elif activity_type == "walk":
            field = "calories_walk"
        else:
            return False

        # Fetch existing value
        res = supabase.table("daily_summary") \
            .select(field) \
            .eq("user_id", user_id) \
            .eq("date", date) \
            .execute()

        # Handle both missing data and NULL values
        current = 0
        if res.data and res.data[0]:
            value = res.data[0].get(field)
            if value is not None:
                current = float(value)

        supabase.table("daily_summary") \
            .update({
                field: current + calories_burned
            }) \
            .eq("user_id", user_id) \
            .eq("date", date) \
            .execute()

        return True

    except Exception as e:
        print(f"❌ Error updating activity: {e}")
        return False

# In database.py - Update this function
@st.cache_data(ttl=300) # Cache for 5 minutes
def get_daily_summaries_range(user_id, start_date, end_date):
    res = supabase.table("daily_summary") \
        .select("*") \
        .eq("user_id", user_id) \
        .gte("date", start_date) \
        .lte("date", end_date) \
        .order("date") \
        .execute()

    if not res.data:
        return []

    # ✅ Source-level normalization: convert None to 0.0 for numeric fields
    numeric_fields = [
        "calories_consumed", "protein", "carbs", "fat", "fiber",
        "calories_walk", "calories_gym", "calories_burned",
        "calorie_deficit", "water_intake_liters", "weight"
    ]

    for row in res.data:
        for field in numeric_fields:
            if row.get(field) is None:
                row[field] = 0.0
                
    return res.data

def create_daily_summary_if_needed(user_id: int, date: str) -> bool:
    try:
        # Check if exists
        exists = supabase.table("daily_summary").select("id").eq("user_id", user_id).eq("date", date).execute()
        
        if not exists.data:
            # Get the target from settings
            settings = get_settings(user_id)
            exercise_goal = settings.get('exercise_calories_target', 0)
            
            supabase.table("daily_summary").insert({
                "user_id": user_id,
                "date": date,
                "exercise_calories_goal": exercise_goal,
                "calories_consumed": 0,
                "water_intake_liters": 0
            }).execute()
        return True
    except Exception as e:
        print(f"❌ Error creating daily summary: {e}")
        return False

# ==================== SETTINGS ====================
@st.cache_data(ttl=600)
def get_settings(user_id):
    defaults = {
        'user_id': user_id,
        'calorie_deficit_constant': 500.0,
        'daily_water_goal_liters': 3.0,
        'activity_level': 'moderate',
        'diet_preference': 'balanced',
        'goal_type': 'weight_loss',
        'target_loss_per_week': 0.5,
        'recommended_daily_calories': 0.0,
        'recommended_protein': 0.0,
        'recommended_carbs': 0.0,
        'recommended_fat': 0.0,
        'exercise_calories_target': 0.0,
        'use_recommendations': 1,
        'custom_calorie_goal': 0.0,
        'custom_protein_goal': 0.0,
        'custom_carbs_goal': 0.0,
        'custom_fat_goal': 0.0,
    }
    
    try:
        res = supabase.table("settings").select("*").eq("user_id", user_id).execute()
        if res.data:
            # Merge DB data over defaults
            return {**defaults, **res.data[0]}
        return defaults
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return defaults


def update_settings(user_id, **kwargs):
    supabase.table("settings").update(kwargs).eq("user_id", user_id).execute()
    # CLEAR THE CACHE
    get_settings.clear(user_id)
    return True