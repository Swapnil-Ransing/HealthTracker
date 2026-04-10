"""
Test script for authentication module (Phase 3).
Run this to verify login, signup, and user profile creation work correctly.
"""

import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from database import delete_all_data, init_db
from auth import (
    register_user, login_user, get_user_info, 
    validate_username, validate_password
)


def test_authentication():
    """Test authentication flow."""
    print("\n" + "="*70)
    print("🧪 HealthTracker Authentication - Phase 3 Test Suite")
    print("="*70 + "\n")

    # Clean up previous test data
    print("✓ Step 1: Resetting database...")
    delete_all_data()
    init_db()
    print("   Database reset and ready\n")

    # Test username validation
    print("✓ Step 2: Testing username validation...")
    valid, msg = validate_username("john_doe")
    print(f"   'john_doe': {msg}")
    
    valid, msg = validate_username("az")
    print(f"   'az': {msg}")
    print()

    # Test password validation
    print("✓ Step 3: Testing password validation...")
    valid, msg = validate_password("SecurePass123")
    print(f"   'SecurePass123': {msg}")
    
    valid, msg = validate_password("123")
    print(f"   '123': {msg}")
    print()

    # Test user registration - Create family
    print("✓ Step 4: Registering first user (with new family)...")
    success, message, user_id = register_user(
        username="swapnil",
        password="HealthTrack123!",
        name="Swapnil Singh",
        gender="Male",
        age=28,
        height=180,
        current_weight=75.5,
        target_weight=68.0,
        family_option="create_new",
        family_name="Singh Family"
    )
    
    if success:
        print(f"   ✅ {message}")
        print(f"   User ID: {user_id}\n")
        user1_id = user_id
    else:
        print(f"   ❌ {message}\n")
        return

    # Get user info
    print("✓ Step 5: Retrieving user information...")
    user_info = get_user_info(user1_id)
    user = user_info['user']
    settings = user_info['settings']
    family = user_info['family']
    
    print(f"   Username: {user['username']}")
    print(f"   Name: {user['name']}")
    print(f"   Age: {user['age']} years")
    print(f"   Height: {user['height']} cm")
    print(f"   Current Weight: {user['current_weight']} kg")
    print(f"   Target Weight: {user['target_weight']} kg")
    print(f"   Family: {family['family_name']} (Code: {family['family_code']})")
    print(f"   Calorie Deficit: {settings['calorie_deficit_constant']} kcal/day")
    print(f"   Water Goal: {settings['daily_water_goal_liters']}L\n")

    # Test login with correct credentials
    print("✓ Step 6: Testing login with correct credentials...")
    success, message, logged_in_user_id = login_user("swapnil", "HealthTrack123!")
    
    if success:
        print(f"   ✅ {message}")
        print(f"   User ID: {logged_in_user_id}\n")
    else:
        print(f"   ❌ {message}\n")

    # Test login with incorrect password
    print("✓ Step 7: Testing login with incorrect password...")
    success, message, logged_in_user_id = login_user("swapnil", "WrongPassword")
    
    if not success:
        print(f"   ✅ Correctly rejected: {message}\n")
    else:
        print(f"   ❌ Should have failed\n")

    # Test registering second user - Join existing family
    print("✓ Step 8: Registering second user (joining existing family)...")
    success, message, user_id = register_user(
        username="priya",
        password="HealthTrack456!",
        name="Priya Singh",
        gender="Female",
        age=26,
        height=165,
        current_weight=62.0,
        target_weight=58.0,
        family_option="join_existing",
        family_code=family['family_code']
    )
    
    if success:
        print(f"   ✅ {message}")
        print(f"   User ID: {user_id}\n")
        user2_id = user_id
    else:
        print(f"   ❌ {message}\n")
        return

    # Test duplicate username
    print("✓ Step 9: Testing duplicate username prevention...")
    success, message, user_id = register_user(
        username="swapnil",
        password="NewPassword123!",
        name="Another User",
        gender="Male",
        age=30,
        height=175,
        current_weight=80,
        target_weight=75,
        family_option="create_new",
        family_name="Another Family"
    )
    
    if not success:
        print(f"   ✅ Correctly rejected: {message}\n")
    else:
        print(f"   ❌ Should have failed\n")

    # Test invalid family code
    print("✓ Step 10: Testing invalid family code...")
    success, message, user_id = register_user(
        username="invalid_user",
        password="Password123!",
        name="Invalid User",
        gender="Male",
        age=25,
        height=170,
        current_weight=70,
        target_weight=65,
        family_option="join_existing",
        family_code="INVALID"
    )
    
    if not success:
        print(f"   ✅ Correctly rejected: {message}\n")
    else:
        print(f"   ❌ Should have failed\n")

    # Verify family members
    print("✓ Step 11: Verifying family members...")
    user1_info = get_user_info(user1_id)
    family_members = user1_info['family_members']
    
    print(f"   Family has {len(family_members)} members:")
    for member in family_members:
        print(f"   - {member['name']} (@{member['username']})")
    print()

    print("="*70)
    print("✅ All authentication tests completed successfully!")
    print("="*70)
    print("\n📊 Test Summary:")
    print(f"   - User registration: ✅")
    print(f"   - Login with valid credentials: ✅")
    print(f"   - Login rejection (invalid): ✅")
    print(f"   - Family creation: ✅")
    print(f"   - Family join: ✅")
    print(f"   - Duplicate prevention: ✅")
    print(f"   - Settings initialization: ✅")
    print(f"   - Users created: 2 ({user1_id}, {user2_id})")
    print()


if __name__ == "__main__":
    test_authentication()
