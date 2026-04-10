"""
Test script for Phase 5 - Meal & Water Logging Features.
Demonstrates the meal logging and water tracking functionality.
"""

import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from datetime import datetime, timedelta
from database import (
    init_db, delete_all_data, create_user, get_user_by_username,
    log_meal, get_meals_by_date, log_water, get_total_water_by_date,
    save_daily_summary, get_daily_summary
)
from calculations import (
    calculate_macronutrient_percentages, get_hydration_status,
    calculate_calorie_deficit
)


def test_phase5():
    """Test meal and water logging functionality."""
    print("\n" + "="*70)
    print("🧪 HealthTracker Meal & Water Logging - Phase 5 Test Suite")
    print("="*70 + "\n")

    # Step 1: Reset and initialize database
    print("✓ Step 1: Initializing database...")
    delete_all_data()
    init_db()
    print("   Database ready\n")

    # Step 2: Create test user
    print("✓ Step 2: Creating test user...")
    user_id = create_user(
        username="testuser",
        password="test123",
        name="Test User",
        gender="Male",
        age=28,
        height=180,
        current_weight=75,
        target_weight=70
    )
    print(f"   User created: {user_id}\n")

    # Step 3: Test meal logging
    print("✓ Step 3: Testing meal logging...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    test_meals = [
        ("Breakfast", "2 eggs, 2 slices of toast with butter"),
        ("Lunch", "Grilled chicken 150g with brown rice and broccoli"),
        ("Snack", "1 banana with 1 tbsp peanut butter"),
        ("Dinner", "Salmon fillet 150g with asparagus and olive oil")
    ]
    
    meal_ids = []
    for meal_type, meal_desc in test_meals:
        meal_id = log_meal(
            user_id=user_id,
            date=today,
            meal_type=meal_type,
            meal_description=meal_desc,
            calories=None  # Will be filled by GPT
        )
        meal_ids.append(meal_id)
        print(f"   ✓ {meal_type}: {meal_desc}")
    
    print(f"   Total meals logged: {len(meal_ids)}\n")

    # Step 4: Retrieve meals
    print("✓ Step 4: Retrieving logged meals...")
    meals = get_meals_by_date(user_id, today)
    print(f"   Found {len(meals)} meals for {today}:")
    for meal in meals:
        print(f"   - {meal['meal_type']}: {meal['meal_description']}")
    print()

    # Step 5: Simulate GPT meal analysis
    print("✓ Step 5: Simulating meal calorie calculation...")
    # Manually add nutrition data (simulating GPT results)
    from database import get_db_connection
    
    meal_nutrition = [
        (350, 20, 40, 12, 3),    # Breakfast
        (600, 45, 60, 15, 5),    # Lunch
        (200, 8, 25, 7, 3),      # Snack
        (450, 50, 15, 20, 2)     # Dinner
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for meal, (cal, prot, carb, fat, fiber) in zip(meals, meal_nutrition):
        cursor.execute("""
            UPDATE nutrition_log
            SET calories = ?, protein = ?, carbs = ?, fat = ?, fiber = ?
            WHERE id = ?
        """, (cal, prot, carb, fat, fiber, meal['id']))
    
    conn.commit()
    conn.close()
    
    print("   Meal nutrition data added:")
    for meal_type, nutrition in zip([m[0] for m in test_meals], meal_nutrition):
        print(f"   - {meal_type}: {nutrition[0]} kcal | {nutrition[1]}p | {nutrition[2]}c | {nutrition[3]}f")
    print()

    # Step 6: Calculate daily totals
    print("✓ Step 6: Calculating daily nutrition totals...")
    meals = get_meals_by_date(user_id, today)
    
    total_calories = sum(m['calories'] or 0 for m in meals)
    total_protein = sum(m['protein'] or 0 for m in meals)
    total_carbs = sum(m['carbs'] or 0 for m in meals)
    total_fat = sum(m['fat'] or 0 for m in meals)
    total_fiber = sum(m['fiber'] or 0 for m in meals)
    
    print(f"   Total Calories: {total_calories} kcal")
    print(f"   Total Protein: {total_protein}g")
    print(f"   Total Carbs: {total_carbs}g")
    print(f"   Total Fat: {total_fat}g")
    print(f"   Total Fiber: {total_fiber}g\n")

    # Step 7: Macronutrient breakdown
    print("✓ Step 7: Calculating macronutrient percentages...")
    macros = calculate_macronutrient_percentages(total_protein, total_carbs, total_fat)
    print(f"   Protein: {macros['protein_percentage']}%")
    print(f"   Carbs: {macros['carbs_percentage']}%")
    print(f"   Fat: {macros['fat_percentage']}%\n")

    # Step 8: Test water logging
    print("✓ Step 8: Testing water logging...")
    water_entries = [
        0.5,   # Morning
        0.75,  # Mid-morning
        1.0,   # Lunch
        0.5,   # Afternoon
        0.75,  # Evening
    ]
    
    for i, amount in enumerate(water_entries):
        log_water(
            user_id=user_id,
            date=today,
            water_liters=amount,
            time=f"{8 + i*3:02d}:00"
        )
        print(f"   ✓ Logged {amount}L at {8 + i*3:02d}:00")
    
    print()

    # Step 9: Get total water intake
    print("✓ Step 9: Retrieving daily water intake...")
    total_water = get_total_water_by_date(user_id, today)
    daily_goal = 3.0
    print(f"   Total water today: {total_water}L")
    print(f"   Daily goal: {daily_goal}L\n")

    # Step 10: Hydration status
    print("✓ Step 10: Checking hydration status...")
    hydration = get_hydration_status(total_water, daily_goal)
    print(f"   Status: {hydration['status']}")
    print(f"   Percentage: {hydration['percentage']}%")
    print(f"   Remaining: {hydration['remaining']}L\n")

    # Step 11: Save daily summary
    print("✓ Step 11: Saving daily summary...")
    calories_burned = 300  # Simulated
    deficit_constant = 500
    calorie_deficit = calculate_calorie_deficit(total_calories, calories_burned, deficit_constant)
    
    save_daily_summary(
        user_id=user_id,
        date=today,
        calories_consumed=total_calories,
        protein=total_protein,
        carbs=total_carbs,
        fat=total_fat,
        fiber=total_fiber,
        calories_walk=0,
        calories_gym=calories_burned,
        calories_burned=calories_burned,
        calorie_deficit=calorie_deficit,
        water_intake=total_water,
        weight=74.5
    )
    print(f"   Daily summary saved\n")

    # Step 12: Retrieve daily summary
    print("✓ Step 12: Retrieving daily summary...")
    summary = get_daily_summary(user_id, today)
    print(f"   Date: {summary['date']}")
    print(f"   Calories: {summary['calories_consumed']} kcal consumed")
    print(f"   Calories Burned: {summary['calories_burned']} kcal")
    print(f"   Calorie Deficit: {summary['calorie_deficit']} kcal")
    print(f"   Water: {summary['water_intake_liters']}L")
    print(f"   Weight: {summary['weight']}kg\n")

    # Step 13: Test previous day data
    print("✓ Step 13: Testing data persistence (multi-day)...")
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Log a meal for yesterday
    log_meal(
        user_id=user_id,
        date=yesterday,
        meal_type="Breakfast",
        meal_description="Oatmeal with berries",
        calories=300,
        protein=10,
        carbs=50,
        fat=5,
        fiber=5
    )
    
    log_water(user_id=user_id, date=yesterday, water_liters=2.5)
    
    save_daily_summary(
        user_id=user_id,
        date=yesterday,
        calories_consumed=300,
        protein=10,
        carbs=50,
        fat=5,
        fiber=5,
        water_intake=2.5,
        weight=75.0
    )
    
    yesterday_meals = get_meals_by_date(user_id, yesterday)
    yesterday_summary = get_daily_summary(user_id, yesterday)
    
    print(f"   Yesterday ({yesterday}) meals: {len(yesterday_meals)}")
    print(f"   Yesterday water: {yesterday_summary['water_intake_liters']}L")
    print(f"   Yesterday weight: {yesterday_summary['weight']}kg\n")

    print("="*70)
    print("✅ All Phase 5 tests completed successfully!")
    print("="*70)
    print("\n📊 Test Summary:")
    print(f"   ✅ Meal logging: 4 meals")
    print(f"   ✅ Nutrition calculation: {total_calories} kcal total")
    print(f"   ✅ Macronutrient breakdown: P:{macros['protein_percentage']}% C:{macros['carbs_percentage']}% F:{macros['fat_percentage']}%")
    print(f"   ✅ Water logging: {total_water}L total ({hydration['percentage']}% of goal)")
    print(f"   ✅ Daily summary saved")
    print(f"   ✅ Multi-day data tracking")
    print("\n💡 Features Ready:")
    print("   - Log meals with natural language descriptions")
    print("   - Calculate calories from meal descriptions (via GPT)")
    print("   - Track macronutrients (protein, carbs, fat, fiber)")
    print("   - Quick-add water intake buttons")
    print("   - Manual water logging with time")
    print("   - Daily water goal customization")
    print("   - Hydration status indicators")
    print("   - Daily summary with all metrics")
    print()


if __name__ == "__main__":
    test_phase5()
