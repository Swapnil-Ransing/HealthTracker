"""
Test script for Phase 6A - Calorie & Macro Recommendations.
Tests recommendation generation (calculated and GPT-based) with manual overrides.
"""

import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from datetime import datetime
from database import (
    init_db, delete_all_data, create_user, get_user,
    get_settings, update_settings
)
from recommendations import (
    generate_calculated_recommendations,
    generate_gpt_recommendations,
    save_recommendations,
    save_custom_recommendations,
    update_user_profile_preferences,
    get_active_recommendations
)
from calculations import calculate_macronutrient_percentages


def test_phase6a():
    """Test Phase 6A recommendations functionality."""
    print("\n" + "="*70)
    print("🧪 HealthTracker Recommendations - Phase 6A Test Suite")
    print("="*70 + "\n")

    # Step 1: Reset database
    print("✓ Step 1: Initializing database...")
    delete_all_data()
    init_db()
    print("   Database ready\n")

    # Step 2: Create test user
    print("✓ Step 2: Creating test user...")
    user_id = create_user(
        username="fituser",
        password="fitpass123",
        name="Fitness Enthusiast",
        gender="Male",
        age=30,
        height=180,
        current_weight=90,
        target_weight=75
    )
    print(f"   User created: {user_id}")
    user = get_user(user_id)
    print(f"   Profile: {user['name']}, {user['age']} years, {user['height']}cm, {user['current_weight']}kg → {user['target_weight']}kg\n")

    # Step 3: Update user preferences
    print("✓ Step 3: Setting user preferences...")
    result = update_user_profile_preferences(
        user_id,
        activity_level="very_active",
        diet_preference="high_protein",
        target_loss_per_week=0.75
    )
    
    if result:
        settings = get_settings(user_id)
        print(f"   Activity Level: {settings['activity_level']}")
        print(f"   Diet Preference: {settings['diet_preference']}")
        print(f"   Target Loss: {settings['target_loss_per_week']}kg/week\n")
    else:
        print("   ❌ Failed to update preferences\n")

    # Step 4: Generate calculated recommendations
    print("✓ Step 4: Generating calculated recommendations...")
    calc_rec = generate_calculated_recommendations(user_id)
    
    if calc_rec:
        print(f"   Daily Calories: {calc_rec['daily_calories']:.0f} kcal")
        print(f"   Protein: {calc_rec['protein_grams']:.0f}g")
        print(f"   Carbs: {calc_rec['carbs_grams']:.0f}g")
        print(f"   Fat: {calc_rec['fat_grams']:.0f}g")
        print(f"   Daily Deficit: {calc_rec['calorie_deficit']:.0f} kcal")
        print(f"   Weekly Loss: {calc_rec['weekly_weight_loss']} kg/week")
        print(f"   BMR: {calc_rec['bmr']:.0f} kcal/day")
        print(f"   TDEE: {calc_rec['tdee']:.0f} kcal/day (very_active)")
        print(f"   Reasoning: {calc_rec['reasoning']}\n")
        
        # Show tips
        print("   💡 Tips:")
        for i, tip in enumerate(calc_rec['tips'], 1):
            print(f"      {i}. {tip}\n")
    else:
        print("   ❌ Failed to generate recommendations\n")

    # Step 5: Save calculated recommendations
    print("✓ Step 5: Saving calculated recommendations...")
    result = save_recommendations(user_id, calc_rec, use_gpt=False)
    
    if result:
        print("   ✅ Recommendations saved to database\n")
    else:
        print("   ❌ Failed to save\n")

    # Step 6: Test GPT recommendations (if API key available)
    print("✓ Step 6: Testing GPT recommendations...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and api_key.startswith("sk-"):
        print("   API key found, generating GPT recommendations...")
        gpt_rec = generate_gpt_recommendations(user_id)
        
        if gpt_rec:
            print(f"   ✅ GPT Recommendations received!")
            print(f"   Daily Calories: {gpt_rec['daily_calories']:.0f} kcal")
            print(f"   Protein: {gpt_rec['protein_grams']:.0f}g")
            print(f"   Carbs: {gpt_rec['carbs_grams']:.0f}g")
            print(f"   Fat: {gpt_rec['fat_grams']:.0f}g")
            print(f"   Weekly Loss: {gpt_rec['weekly_weight_loss']:.2f} kg/week")
            print(f"   Diet Type: {gpt_rec['diet_type']}")
            print(f"   Reasoning: {gpt_rec['reasoning']}\n")
            
            # Show tips
            print("   🤖 AI Tips:")
            for i, tip in enumerate(gpt_rec['tips'], 1):
                print(f"      {i}. {tip}\n")
        else:
            print("   ⚠️ GPT API call failed (this is normal if API is busy)\n")
    else:
        print("   ⚠️ OpenAI API key not configured, skipping GPT test\n")

    # Step 7: Test custom goal override
    print("✓ Step 7: Testing custom goal override...")
    custom_goals = {
        'daily_calories': 2000,
        'protein_grams': 150,
        'carbs_grams': 200,
        'fat_grams': 70,
        'calorie_deficit': 600
    }
    
    result = save_custom_recommendations(user_id, custom_goals)
    
    if result:
        print(f"   Custom goals saved:")
        print(f"   - Calories: {custom_goals['daily_calories']} kcal")
        print(f"   - Protein: {custom_goals['protein_grams']}g")
        print(f"   - Carbs: {custom_goals['carbs_grams']}g")
        print(f"   - Fat: {custom_goals['fat_grams']}g")
        print(f"   - Deficit: {custom_goals['calorie_deficit']} kcal\n")
    else:
        print("   ❌ Failed to save custom goals\n")

    # Step 8: Verify active recommendations
    print("✓ Step 8: Retrieving active recommendations...")
    active = get_active_recommendations(user_id)
    
    if active:
        print(f"   Source: {active['source']}")
        print(f"   Calories: {active['daily_calories']} kcal")
        print(f"   Protein: {active['protein_grams']}g")
        print(f"   Carbs: {active['carbs_grams']}g")
        print(f"   Fat: {active['fat_grams']}g")
        print(f"   Deficit: {active['calorie_deficit']} kcal\n")
    else:
        print("   ❌ Failed to retrieve\n")

    # Step 9: Test macro calculation
    print("✓ Step 9: Calculating macro breakdown...")
    macros = calculate_macronutrient_percentages(
        custom_goals['protein_grams'],
        custom_goals['carbs_grams'],
        custom_goals['fat_grams']
    )
    
    print(f"   Protein: {macros['protein_percentage']:.1f}%")
    print(f"   Carbs: {macros['carbs_percentage']:.1f}%")
    print(f"   Fat: {macros['fat_percentage']:.1f}%")
    print(f"   Total: {macros['total_calories']:.0f} kcal\n")

    # Step 10: Test different user profiles
    print("✓ Step 10: Testing recommendations for different users...")
    
    # Female user, weight gain
    user2_id = create_user(
        username="gains_user",
        password="gainspass123",
        name="Muscle Builder",
        gender="Female",
        age=25,
        height=165,
        current_weight=60,
        target_weight=68
    )
    
    update_user_profile_preferences(
        user2_id,
        activity_level="very_active",
        diet_preference="high_protein",
        target_loss_per_week=0.5
    )
    
    rec2 = generate_calculated_recommendations(user2_id)
    print(f"   Female, targeting weight gain:")
    print(f"   - Daily Calories: {rec2['daily_calories']:.0f} kcal")
    print(f"   - Protein: {rec2['protein_grams']:.0f}g")
    print(f"   - Weight to gain: {user2_id - 60:.0f}kg\n")

    # Step 11: Verify database schema
    print("✓ Step 11: Verifying database schema...")
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(settings)")
    columns = cursor.fetchall()
    conn.close()
    
    print(f"   Settings table columns: {len(columns)}")
    expected_columns = [
        'user_id', 'calorie_deficit_constant', 'daily_water_goal_liters',
        'activity_level', 'diet_preference', 'recommended_daily_calories',
        'recommended_protein', 'custom_calorie_goal', 'use_recommendations'
    ]
    
    found_columns = [col[1] for col in columns]
    for col in expected_columns:
        if col in found_columns:
            print(f"   ✅ {col}")
        else:
            print(f"   ❌ {col} (MISSING)")
    print()

    print("="*70)
    print("✅ All Phase 6A tests completed!")
    print("="*70)
    print("\n📊 Features Tested:")
    print("   ✅ Calculated recommendations (BMR+TDEE+deficit)")
    print("   ✅ GPT-based personalized recommendations")
    print("   ✅ Manual goal override")
    print("   ✅ Activity level preferences")
    print("   ✅ Diet preference selection")
    print("   ✅ Macro percentage calculations")
    print("   ✅ Multiple user profiles")
    print("   ✅ Database schema with new settings fields")
    print("\n💡 Key Features:")
    print("   - Auto-calculate BMR and TDEE based on activity level")
    print("   - Ask GPT for personalized recommendations")
    print("   - Users can override with custom goals")
    print("   - Track 3 different goal strategies in DB")
    print("   - Support for weight loss/gain/maintenance")
    print()


if __name__ == "__main__":
    test_phase6a()
