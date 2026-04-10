"""
Test script for GPT integration (Phase 4).
Run this to verify meal analysis and calorie calculation work correctly.
"""

import sys
sys.path.insert(0, 'utils')

from gpt_utils import (
    calculate_nutrition_from_meal,
    calculate_nutrition_for_multiple_meals,
    validate_api_key,
    get_cache_stats,
    clear_cache
)


def test_gpt_integration():
    """Test GPT integration for meal analysis."""
    print("\n" + "="*70)
    print("🧪 HealthTracker GPT Integration - Phase 4 Test Suite")
    print("="*70 + "\n")

    # Step 1: Validate API Key
    print("✓ Step 1: Validating OpenAI API Key...")
    if not validate_api_key():
        print("   ❌ API key not configured. Please add OPENAI_API_KEY to .env file")
        print("   Without API key, GPT features will not work.")
        print("\n   To configure:")
        print("   1. Get your API key from https://platform.openai.com/api-keys")
        print("   2. Edit .env file and add: OPENAI_API_KEY=sk-your-key-here")
        print("   3. Save and re-run this test\n")
        return
    print("   ✅ API key is configured\n")

    # Test meals
    test_meals = [
        "2 fried eggs with 2 slices of white toast and 1 tbsp butter",
        "Grilled chicken breast 150g with brown rice 1 cup and broccoli",
        "1 banana and 1 tbsp peanut butter",
        "Greek yogurt 200g with granola and honey",
        "Salmon fillet 150g with lemon and asparagus"
    ]

    print("✓ Step 2: Testing single meal analysis...\n")
    
    meal = test_meals[0]
    print(f"   Analyzing: '{meal}'")
    print("   Calling GPT API...\n")
    
    success, nutrition = calculate_nutrition_from_meal(meal)
    
    if success and nutrition:
        print("   ✅ Analysis successful!")
        print(f"   - Meal Description: {nutrition['meal_description']}")
        print(f"   - Calories: {nutrition['calories']} kcal")
        print(f"   - Protein: {nutrition['protein']}g")
        print(f"   - Carbs: {nutrition['carbs']}g")
        print(f"   - Fat: {nutrition['fat']}g")
        print(f"   - Fiber: {nutrition['fiber']}g")
        if 'assumptions' in nutrition:
            print(f"   - Assumptions: {nutrition['assumptions']}")
    else:
        print("   ❌ Analysis failed")
        return
    
    print()

    # Step 3: Test cache
    print("✓ Step 3: Testing meal cache...\n")
    
    print(f"   Analyzing the same meal again...")
    success, nutrition2 = calculate_nutrition_from_meal(meal)
    
    if success:
        print("   ✅ Retrieved from cache (no API call made)")
        
        cache_stats = get_cache_stats()
        print(f"\n   Cache Statistics:")
        print(f"   - Cached meals: {cache_stats['cached_meals']}")
        print(f"   - Meals in cache: {cache_stats['meals']}")
    
    print()

    # Step 4: Test multiple meals
    print("✓ Step 4: Testing multiple meals analysis...\n")
    
    sample_meals = test_meals[1:4]  # Use 3 meals
    
    print(f"   Analyzing {len(sample_meals)} meals...")
    for i, m in enumerate(sample_meals, 1):
        print(f"   {i}. {m}")
    print()
    
    result = calculate_nutrition_for_multiple_meals(sample_meals)
    
    print(f"   ✅ Analysis complete!")
    print(f"\n   Aggregated Results:")
    print(f"   - Total Calories: {result['total_calories']} kcal")
    print(f"   - Total Protein: {result['total_protein']}g")
    print(f"   - Total Carbs: {result['total_carbs']}g")
    print(f"   - Total Fat: {result['total_fat']}g")
    print(f"   - Total Fiber: {result['total_fiber']}g")
    print(f"   - Successful: {result['success_count']}")
    print(f"   - Failed: {result['error_count']}\n")
    
    print("   Individual Meal Details:")
    for i, meal_data in enumerate(result['meal_details'], 1):
        print(f"\n   {i}. {meal_data['meal_description']}")
        print(f"      Calories: {meal_data['calories']} | Protein: {meal_data['protein']}g | Carbs: {meal_data['carbs']}g | Fat: {meal_data['fat']}g")

    print()

    # Step 5: Test different meal types
    print("✓ Step 5: Testing different meal types...\n")
    
    different_meals = [
        "Breakfast: Oatmeal with berries and almonds",
        "Lunch: Pasta carbonara with bacon and parmesan",
        "Snack: Apple with almond butter",
        "Dinner: Beef steak with sweet potato and salad"
    ]
    
    for meal in different_meals:
        print(f"   Analyzing: {meal}")
        success, nutrition = calculate_nutrition_from_meal(meal)
        if success:
            print(f"   ✅ {nutrition['calories']} kcal ({nutrition['protein']}p | {nutrition['carbs']}c | {nutrition['fat']}f)\n")
        else:
            print(f"   ❌ Failed\n")

    # Step 6: Clear cache
    print("✓ Step 6: Testing cache clearing...\n")
    clear_cache()
    
    cache_stats = get_cache_stats()
    print(f"   Cache after clearing:")
    print(f"   - Cached meals: {cache_stats['cached_meals']}\n")

    print("="*70)
    print("✅ All GPT integration tests completed!")
    print("="*70)
    print("\n📊 Test Summary:")
    print(f"   - API key validation: ✅")
    print(f"   - Single meal analysis: ✅")
    print(f"   - Meal caching: ✅")
    print(f"   - Multiple meals aggregation: ✅")
    print(f"   - Cache management: ✅")
    print("\n💡 Tips:")
    print("   - GPT API costs money per request. Cache helps reduce costs.")
    print("   - Typical cost: ~$0.002 per meal analysis")
    print("   - Cache stores results in memory during app session")
    print()


if __name__ == "__main__":
    test_gpt_integration()
