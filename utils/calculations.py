"""
Calculations module for health metrics, calorie expenditure, and weight tracking.
Handles BMR, calorie burn rates, deficit calculations, and health recommendations.
"""

from typing import Dict, Tuple


def calculate_bmr(gender: str, age: int, height: float, weight: float) -> float:
    """
    Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor equation.
    
    Args:
        gender: "Male" or "Female"
        age: Age in years
        height: Height in cm
        weight: Weight in kg
    
    Returns:
        BMR in kcal/day
    """
    if gender.lower() == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # Female
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    return round(bmr, 2)


def calculate_tdee(bmr: float, activity_level: str = "moderate") -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE).
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: "sedentary", "light", "moderate", "very_active", "extremely_active"
    
    Returns:
        TDEE in kcal/day
    """
    activity_multipliers = {
        "sedentary": 1.2,           # Little or no exercise
        "light": 1.375,              # 1-3 days/week
        "moderate": 1.55,            # 3-5 days/week
        "very_active": 1.725,        # 6-7 days/week
        "extremely_active": 1.9      # Physical job or training twice per day
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    tdee = bmr * multiplier
    
    return round(tdee, 2)


def calculate_calories_for_weight_loss(tdee: float, goal_weight_loss_per_week: float = 0.5) -> Dict:
    """
    Calculate calorie targets for weight loss.
    
    Args:
        tdee: Total Daily Energy Expenditure
        goal_weight_loss_per_week: Target weight loss per week in kg (0.25-1.0 recommended)
    
    Returns:
        {
            'daily_deficit': float,           # Daily calorie deficit needed
            'daily_calorie_intake': float,    # Daily calorie target
            'estimated_loss_per_month': float # Estimated weight loss per month
        }
    """
    # 1 kg = 7700 calories
    calories_per_kg = 7700
    daily_deficit = (goal_weight_loss_per_week * calories_per_kg) / 7
    daily_calorie_intake = tdee - daily_deficit
    
    # Ensure minimum calorie intake (1200 for females, 1500 for males typically)
    daily_calorie_intake = max(daily_calorie_intake, 1200)
    
    return {
        'daily_deficit': round(daily_deficit, 2),
        'daily_calorie_intake': round(daily_calorie_intake, 2),
        'estimated_loss_per_month': round(goal_weight_loss_per_week * 4.33, 1)
    }


def calculate_calories_burned_walking(distance_km: float = None, duration_minutes: float = None, 
                                      body_weight_kg: float = 70) -> float:
    """
    Calculate calories burned during walking.
    
    Args:
        distance_km: Distance walked in kilometers (OR)
        duration_minutes: Duration in minutes (if distance not provided)
        body_weight_kg: Body weight in kg (for more accurate calculation)
    
    Returns:
        Estimated calories burned
    """
    if distance_km:
        # Approximate: 60-80 calories per km for 70kg person
        # Adjusted for body weight: calories ∝ weight
        base_calories_per_km = 70
        adjusted = (body_weight_kg / 70) * base_calories_per_km
        return round(distance_km * adjusted, 2)
    
    elif duration_minutes:
        # Approximate: 4-5 calories per minute for 70kg person
        base_calories_per_min = 4.5
        adjusted = (body_weight_kg / 70) * base_calories_per_min
        return round(duration_minutes * adjusted, 2)
    
    return 0.0


def calculate_calories_burned_gym(duration_minutes: float, intensity: float = 1.0,
                                  body_weight_kg: float = 70) -> float:
    """
    Calculate calories burned during gym workouts.
    
    Args:
        duration_minutes: Duration of workout in minutes
        intensity: Intensity multiplier (0.5=light, 1.0=moderate, 1.5=intense)
                  or string ("light", "moderate", "intense") for backward compatibility
        body_weight_kg: Body weight in kg
    
    Returns:
        Estimated calories burned
    """
    # Handle string input for backward compatibility
    if isinstance(intensity, str):
        intensity_map = {
            "light": 0.5,
            "moderate": 1.0,
            "intense": 1.5
        }
        intensity = intensity_map.get(intensity.lower(), 1.0)
    
    # Base rate: 8 cal/min at 70kg body weight, moderate intensity
    base_rate = 8.0
    adjusted_rate = (body_weight_kg / 70) * base_rate * intensity
    
    return round(duration_minutes * adjusted_rate, 2)


def calculate_calorie_deficit(calories_consumed: float, calories_burned: float, 
                             deficit_constant: float = 500) -> float:
    """
    Calculate daily calorie deficit.
    
    Formula: Calorie Deficit = Calories Consumed - Calories Burned - Deficit Constant
    
    Args:
        calories_consumed: Total calories consumed in kcal
        calories_burned: Total calories burned in kcal
        deficit_constant: User's deficit constant in kcal (default 500 for ~0.5kg/week loss)
    
    Returns:
        Calorie deficit (negative = surplus, positive = deficit)
    """
    deficit = calories_consumed - calories_burned - deficit_constant
    return round(deficit, 2)


def calculate_projected_weight_change(daily_deficits: list, current_weight: float) -> Dict:
    """
    Calculate projected weight change based on daily deficits.
    
    Args:
        daily_deficits: List of daily calorie deficits
        current_weight: Current weight in kg
    
    Returns:
        {
            'average_daily_deficit': float,
            'weekly_deficit': float,
            'projected_weekly_loss': float,
            'projected_monthly_loss': float,
            'projected_weight_in_month': float
        }
    """
    if not daily_deficits:
        return {
            'average_daily_deficit': 0,
            'weekly_deficit': 0,
            'projected_weekly_loss': 0,
            'projected_monthly_loss': 0,
            'projected_weight_in_month': current_weight
        }
    
    avg_daily_deficit = sum(daily_deficits) / len(daily_deficits)
    weekly_deficit = avg_daily_deficit * 7
    weekly_loss = weekly_deficit / 7700  # 1 kg = 7700 calories
    monthly_loss = weekly_loss * 4.33
    
    return {
        'average_daily_deficit': round(avg_daily_deficit, 2),
        'weekly_deficit': round(weekly_deficit, 2),
        'projected_weekly_loss': round(weekly_loss, 2),
        'projected_monthly_loss': round(monthly_loss, 2),
        'projected_weight_in_month': round(current_weight - monthly_loss, 2)
    }


def calculate_macronutrient_percentages(protein_g: float, carbs_g: float, fat_g: float) -> Dict:
    """
    Calculate macronutrient percentages from grams.
    
    Args:
        protein_g: Protein in grams
        carbs_g: Carbohydrates in grams
        fat_g: Fat in grams
    
    Returns:
        {
            'protein_percentage': float,
            'carbs_percentage': float,
            'fat_percentage': float,
            'total_calories': float
        }
    """
    # Calorie values per gram: Protein=4, Carbs=4, Fat=9
    protein_calories = protein_g * 4
    carbs_calories = carbs_g * 4
    fat_calories = fat_g * 9
    total_calories = protein_calories + carbs_calories + fat_calories
    
    if total_calories == 0:
        return {
            'protein_percentage': 0,
            'carbs_percentage': 0,
            'fat_percentage': 0,
            'total_calories': 0
        }
    
    return {
        'protein_percentage': round((protein_calories / total_calories) * 100, 1),
        'carbs_percentage': round((carbs_calories / total_calories) * 100, 1),
        'fat_percentage': round((fat_calories / total_calories) * 100, 1),
        'total_calories': round(total_calories, 2)
    }


def get_hydration_status(water_consumed_liters: float, daily_goal_liters: float = 3.0) -> Dict:
    """
    Determine hydration status based on water intake.
    
    Args:
        water_consumed_liters: Total water consumed
        daily_goal_liters: Daily water goal (default 3L)
    
    Returns:
        {
            'status': str,          # "Optimal", "Low", "High"
            'percentage': float,    # % of daily goal
            'remaining': float      # Liters remaining to goal
        }
    """
    percentage = (water_consumed_liters / daily_goal_liters) * 100
    remaining = max(0, daily_goal_liters - water_consumed_liters)
    
    if percentage < 50:
        status = "Low ⚠️"
    elif 50 <= percentage < 100:
        status = "Good 💧"
    elif 100 <= percentage < 110:
        status = "Optimal 🎯"
    else:
        status = "High 💦"
    
    return {
        'status': status,
        'percentage': round(percentage, 1),
        'remaining': round(remaining, 2)
    }


def calculate_macronutrient_targets(daily_calories: float, diet_type: str = "balanced") -> Dict:
    """
    Calculate daily macronutrient targets based on diet type.
    
    Args:
        daily_calories: Daily calorie target
        diet_type: "balanced", "high_protein", "low_carb", "vegetarian"
    
    Returns:
        {
            'protein_g': float,
            'carbs_g': float,
            'fat_g': float,
            'description': str
        }
    """
    if diet_type == "high_protein":
        protein_pct, carbs_pct, fat_pct = 0.35, 0.40, 0.25
        description = "High protein for muscle building"
    elif diet_type == "low_carb":
        protein_pct, carbs_pct, fat_pct = 0.30, 0.25, 0.45
        description = "Low carb for steady energy"
    elif diet_type == "vegetarian":
        protein_pct, carbs_pct, fat_pct = 0.20, 0.50, 0.30
        description = "Vegetarian-friendly macro split"
    else:  # balanced
        protein_pct, carbs_pct, fat_pct = 0.25, 0.50, 0.25
        description = "Balanced macro distribution"
    
    protein_g = round((daily_calories * protein_pct) / 4, 1)
    carbs_g = round((daily_calories * carbs_pct) / 4, 1)
    fat_g = round((daily_calories * fat_pct) / 9, 1)
    
    return {
        'protein_g': protein_g,
        'carbs_g': carbs_g,
        'fat_g': fat_g,
        'description': description
    }


if __name__ == "__main__":
    # Example usage
    print("Calculations module loaded successfully!")
    
    # Example: Calculate BMR and TDEE for a 30-year-old male, 180cm, 75kg
    bmr = calculate_bmr("Male", 30, 180, 75)
    print(f"BMR: {bmr} kcal/day")
    
    tdee = calculate_tdee(bmr, "moderate")
    print(f"TDEE: {tdee} kcal/day")
    
    # Calculate weight loss targets
    loss_plan = calculate_calories_for_weight_loss(tdee)
    print(f"For 0.5kg/week loss: {loss_plan}")
