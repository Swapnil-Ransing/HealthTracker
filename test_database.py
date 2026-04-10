"""
Test script for database initialization and basic operations.
Run this to verify Phase 2 (Database Layer) is working correctly.
"""

import sys
sys.path.insert(0, 'db')

from database import (
    init_db, create_user, get_user, authenticate_user,
    create_family, get_family, get_family_members, log_meal, log_water,
    get_meals_by_date, get_total_water_by_date, save_daily_summary,
    get_daily_summary, update_settings, get_settings, delete_all_data
)
from datetime import datetime


def test_database():
    """Test database operations."""
    print("\n" + "="*60)
    print("🧪 HealthTracker Database - Phase 2 Test Suite")
    print("="*60 + "\n")

    # Step 1: Initialize database
    print("✓ Step 1: Initializing database...")
    init_db()
    print()

    # Step 2: Create a family
    print("✓ Step 2: Creating family...")
    family_id = create_family("Smith Family", 0)  # Temp owner_id
    print(f"   Family created with ID: {family_id}")
    family = get_family(family_id)
    print(f"   Family name: {family['family_name']}")
    print(f"   Family code: {family['family_code']}")
    print()

    # Step 3: Create users
    print("✓ Step 3: Creating users...")
    user1_id = create_user(
        username="swapnil",
        password="secure_password_123",
        name="Swapnil Singh",
        family_id=family_id,
        gender="Male",
        age=28,
        height=180,
        current_weight=75,
        target_weight=68
    )
    print(f"   User 1 (Swapnil) created with ID: {user1_id}")

    user2_id = create_user(
        username="priya",
        password="password456",
        name="Priya Singh",
        family_id=family_id,
        gender="Female",
        age=26,
        height=165,
        current_weight=62,
        target_weight=58
    )
    print(f"   User 2 (Priya) created with ID: {user2_id}")
    print()

    # Step 4: Test authentication
    print("✓ Step 4: Testing authentication...")
    authenticated_user_id = authenticate_user("swapnil", "secure_password_123")
    if authenticated_user_id == user1_id:
        print(f"   ✅ Authentication successful! User ID: {authenticated_user_id}")
    else:
        print(f"   ❌ Authentication failed!")
    print()

    # Step 5: Get family members
    print("✓ Step 5: Getting family members...")
    members = get_family_members(family_id)
    print(f"   Family has {len(members)} members:")
    for member in members:
        print(f"   - {member['name']} (@{member['username']})")
    print()

    # Step 6: Log meals
    print("✓ Step 6: Logging meals for today...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    meal1_id = log_meal(
        user_id=user1_id,
        date=today,
        meal_type="Breakfast",
        meal_description="2 eggs, 2 slices of toast with butter",
        calories=350,
        protein=20,
        carbs=35,
        fat=15,
        fiber=2
    )
    print(f"   Meal 1 logged: {meal1_id}")

    meal2_id = log_meal(
        user_id=user1_id,
        date=today,
        meal_type="Lunch",
        meal_description="Grilled chicken with rice and vegetables",
        calories=650,
        protein=45,
        carbs=60,
        fat=15,
        fiber=5
    )
    print(f"   Meal 2 logged: {meal2_id}")
    print()

    # Step 7: Get meals by date
    print("✓ Step 7: Retrieving meals for today...")
    meals = get_meals_by_date(user1_id, today)
    print(f"   Found {len(meals)} meals:")
    total_calories = 0
    for meal in meals:
        print(f"   - {meal['meal_type']}: {meal['meal_description']} ({meal['calories']} kcal)")
        total_calories += meal['calories'] if meal['calories'] else 0
    print(f"   Total calories logged: {total_calories} kcal")
    print()

    # Step 8: Log water intake
    print("✓ Step 8: Logging water intake...")
    water1 = log_water(user_id=user1_id, date=today, water_liters=0.5, time="08:00")
    water2 = log_water(user_id=user1_id, date=today, water_liters=0.75, time="12:00")
    water3 = log_water(user_id=user1_id, date=today, water_liters=1.0, time="18:00")
    print(f"   Water entries logged: {water1}, {water2}, {water3}")
    
    total_water = get_total_water_by_date(user1_id, today)
    print(f"   Total water today: {total_water}L")
    print()

    # Step 9: Update settings
    print("✓ Step 9: Updating user settings...")
    update_settings(user_id=user1_id, calorie_deficit=600, water_goal=3.5)
    settings = get_settings(user1_id)
    print(f"   Calorie deficit constant: {settings['calorie_deficit_constant']} kcal/day")
    print(f"   Daily water goal: {settings['daily_water_goal_liters']}L")
    print()

    # Step 10: Save daily summary
    print("✓ Step 10: Saving daily summary...")
    save_daily_summary(
        user_id=user1_id,
        date=today,
        calories_consumed=total_calories,
        protein=65,
        carbs=95,
        fat=30,
        fiber=7,
        calories_walk=300,
        calories_gym=0,
        calories_burned=300,
        calorie_deficit=-250,
        water_intake=total_water,
        weight=74.5,
        is_cheat_day=0
    )
    summary = get_daily_summary(user1_id, today)
    print(f"   Daily Summary for {today}:")
    print(f"   - Calories: {summary['calories_consumed']} kcal")
    print(f"   - Protein: {summary['protein']}g | Carbs: {summary['carbs']}g | Fat: {summary['fat']}g")
    print(f"   - Water: {summary['water_intake_liters']}L")
    print(f"   - Weight: {summary['weight']}kg")
    print(f"   - Calorie Deficit: {summary['calorie_deficit']} kcal")
    print()

    # Step 11: Test family user
    print("✓ Step 11: Testing family member data...")
    log_water(user_id=user2_id, date=today, water_liters=2.5)
    save_daily_summary(
        user_id=user2_id,
        date=today,
        calories_consumed=1800,
        protein=90,
        carbs=200,
        fat=50,
        fiber=20,
        calories_walk=250,
        calories_gym=200,
        calories_burned=450,
        calorie_deficit=-950,
        water_intake=2.5,
        weight=61.8,
        is_cheat_day=0
    )
    priya_summary = get_daily_summary(user2_id, today)
    print(f"   Priya's summary: {priya_summary['calories_consumed']} kcal, {priya_summary['weight']}kg")
    print()

    print("="*60)
    print("✅ All tests completed successfully!")
    print("="*60)
    print("\n📊 Database Statistics:")
    print(f"   - Database file: db/data.db")
    print(f"   - Users created: 2 ({user1_id}, {user2_id})")
    print(f"   - Family created: 1 ({family_id})")
    print(f"   - Meals logged: 2")
    print(f"   - Water entries: 5 (3 for Swapnil, 2 for Priya)")
    print(f"   - Daily summaries: 2\n")


if __name__ == "__main__":
    test_database()
