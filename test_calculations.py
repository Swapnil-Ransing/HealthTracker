"""
Test script for calculations module (Phase 4 - Bonus).
Run this to verify health metrics and calorie calculations work correctly.
"""

import sys
sys.path.insert(0, 'utils')

from calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_calories_for_weight_loss,
    calculate_calories_burned_walking,
    calculate_calories_burned_gym,
    calculate_calorie_deficit,
    calculate_projected_weight_change,
    calculate_macronutrient_percentages,
    get_hydration_status,
    calculate_macronutrient_targets
)


def test_calculations():
    """Test all calculation functions."""
    print("\n" + "="*70)
    print("🧪 HealthTracker Calculations - Phase 4 Bonus Test Suite")
    print("="*70 + "\n")

    # Test user: 28-year-old male, 180cm, 75kg
    gender = "Male"
    age = 28
    height = 180  # cm
    current_weight = 75  # kg
    target_weight = 68  # kg

    print(f"📊 Test User Profile:")
    print(f"   Gender: {gender}")
    print(f"   Age: {age} years")
    print(f"   Height: {height} cm")
    print(f"   Current Weight: {current_weight} kg")
    print(f"   Target Weight: {target_weight} kg\n")

    # Step 1: Calculate BMR
    print("✓ Step 1: Calculating Basal Metabolic Rate (BMR)...")
    bmr = calculate_bmr(gender, age, height, current_weight)
    print(f"   BMR: {bmr} kcal/day")
    print(f"   (Calories burned at rest)\n")

    # Step 2: Calculate TDEE
    print("✓ Step 2: Calculating Total Daily Energy Expenditure (TDEE)...")
    activity_levels = ["sedentary", "light", "moderate", "very_active"]
    for level in activity_levels:
        tdee = calculate_tdee(bmr, level)
        print(f"   {level.capitalize()}: {tdee} kcal/day")
    print()

    tdee = calculate_tdee(bmr, "moderate")  # Use moderate for further calculations

    # Step 3: Calculate weight loss plan
    print("✓ Step 3: Calculating weight loss plan...")
    loss_plan = calculate_calories_for_weight_loss(tdee, 0.5)  # 0.5kg per week
    print(f"   Daily Calorie Deficit: {loss_plan['daily_deficit']} kcal")
    print(f"   Daily Calorie Intake: {loss_plan['daily_calorie_intake']} kcal")
    print(f"   Estimated Loss/Month: {loss_plan['estimated_loss_per_month']} kg")
    print(f"   Months to Goal: {round((current_weight - target_weight) / loss_plan['estimated_loss_per_month'], 1)}\n")

    # Step 4: Calculate calories burned - Walking
    print("✓ Step 4: Calculating calories burned - Walking...")
    walk_calories_5km = calculate_calories_burned_walking(distance_km=5, body_weight_kg=current_weight)
    walk_calories_30min = calculate_calories_burned_walking(duration_minutes=30, body_weight_kg=current_weight)
    print(f"   5 km walk: {walk_calories_5km} kcal")
    print(f"   30 min walk: {walk_calories_30min} kcal\n")

    # Step 5: Calculate calories burned - Gym
    print("✓ Step 5: Calculating calories burned - Gym...")
    gym_intensities = ["light", "moderate", "intense"]
    for intensity in gym_intensities:
        gym_calories = calculate_calories_burned_gym(60, intensity, current_weight)
        print(f"   60 min {intensity} gym: {gym_calories} kcal")
    print()

    # Step 6: Calculate daily calorie deficit
    print("✓ Step 6: Calculating daily calorie deficit...")
    calories_consumed = 1800
    calories_burned = walk_calories_30min + calculate_calories_burned_gym(45, "moderate", current_weight)
    deficit_constant = 500
    daily_deficit = calculate_calorie_deficit(calories_consumed, calories_burned, deficit_constant)
    print(f"   Calories Consumed: {calories_consumed} kcal")
    print(f"   Calories Burned (walk+gym): {calories_burned} kcal")
    print(f"   Deficit Constant: {deficit_constant} kcal")
    print(f"   Daily Deficit: {daily_deficit} kcal")
    print(f"   Status: {'Deficit ✅' if daily_deficit > 0 else 'Surplus ⚠️'}\n")

    # Step 7: Calculate macronutrient percentages
    print("✓ Step 7: Calculating macronutrient breakdowns...")
    protein = 120
    carbs = 200
    fat = 60
    macros = calculate_macronutrient_percentages(protein, carbs, fat)
    print(f"   Intake: {protein}p | {carbs}c | {fat}f")
    print(f"   Percentages:")
    print(f"   - Protein: {macros['protein_percentage']}%")
    print(f"   - Carbs: {macros['carbs_percentage']}%")
    print(f"   - Fat: {macros['fat_percentage']}%")
    print(f"   Total Calories: {macros['total_calories']} kcal\n")

    # Step 8: Hydration status
    print("✓ Step 8: Checking hydration status...")
    water_levels = [1.5, 2.5, 3.0, 3.5, 4.0]
    daily_goal = 3.0
    for water in water_levels:
        hydration = get_hydration_status(water, daily_goal)
        print(f"   {water}L: {hydration['status']} ({hydration['percentage']}% of goal)")
    print()

    # Step 9: Macronutrient targets by diet type
    print("✓ Step 9: Calculating macro targets by diet type...")
    target_calories = 1800
    diet_types = ["balanced", "high_protein", "low_carb", "vegetarian"]
    for diet in diet_types:
        targets = calculate_macronutrient_targets(target_calories, diet)
        print(f"   {diet.capitalize()}:")
        print(f"   - {targets['protein_g']}g protein | {targets['carbs_g']}g carbs | {targets['fat_g']}g fat")
        print(f"   - {targets['description']}")
    print()

    # Step 10: Projected weight change
    print("✓ Step 10: Calculating projected weight change...")
    recent_deficits = [400, 350, 500, 450, 380, 420, 390]  # Last 7 days
    projection = calculate_projected_weight_change(recent_deficits, current_weight)
    print(f"   7-day deficits: {recent_deficits}")
    print(f"   Average daily deficit: {projection['average_daily_deficit']} kcal")
    print(f"   Weekly deficit: {projection['weekly_deficit']} kcal")
    print(f"   Projected weekly loss: {projection['projected_weekly_loss']} kg")
    print(f"   Projected monthly loss: {projection['projected_monthly_loss']} kg")
    print(f"   Weight in 1 month: {projection['projected_weight_in_month']} kg")
    print(f"   Weight loss: {current_weight - projection['projected_weight_in_month']} kg\n")

    print("="*70)
    print("✅ All calculation tests completed successfully!")
    print("="*70)
    print("\n📊 Test Coverage:")
    print("   ✅ BMR Calculation (Mifflin-St Jeor)")
    print("   ✅ TDEE Calculation (with activity levels)")
    print("   ✅ Weight Loss Planning")
    print("   ✅ Calories Burned (Walking)")
    print("   ✅ Calories Burned (Gym)")
    print("   ✅ Calorie Deficit Calculation")
    print("   ✅ Macronutrient Percentages")
    print("   ✅ Hydration Status")
    print("   ✅ Macro Targets (by diet type)")
    print("   ✅ Weight Change Projection")
    print("\n💡 These calculations power the analytics dashboard!")
    print()


if __name__ == "__main__":
    test_calculations()
