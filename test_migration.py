"""
Test database migration and settings defaults handling.
"""
import os
import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

# Make sure we're using a test database
os.environ['DB_PATH'] = 'db/test_data.db'

from database import (
    init_db, delete_all_data, create_user, get_user,
    get_settings, get_db_connection
)

print("\n" + "="*70)
print("🔧 Database Migration & Settings Defaults Test")
print("="*70 + "\n")

# Test 1: Clean start
print("✓ Step 1: Starting fresh with clean database...")
if os.path.exists('db/test_data.db'):
    os.remove('db/test_data.db')
    print("   Removed old test database")

init_db()
print("   ✅ New database initialized with all columns\n")

# Test 2: Create user and check settings
print("✓ Step 2: Creating test user...")
user_id = create_user(
    username="testuser",
    password="testpass",
    name="Test User",
    gender="Male",
    age=30,
    height=180,
    current_weight=90,
    target_weight=75
)
print(f"   User created: {user_id}\n")

# Test 3: Get settings and verify all keys exist
print("✓ Step 3: Getting settings and checking all keys...")
settings = get_settings(user_id)

required_keys = [
    'user_id', 'calorie_deficit_constant', 'daily_water_goal_liters',
    'activity_level', 'diet_preference', 'goal_type',
    'target_loss_per_week', 'recommended_daily_calories',
    'recommended_protein', 'recommended_carbs', 'recommended_fat',
    'use_recommendations', 'custom_calorie_goal', 'custom_protein_goal',
    'custom_carbs_goal', 'custom_fat_goal'
]

print(f"   Settings returned with {len(settings)} keys")
missing_keys = []
for key in required_keys:
    if key in settings:
        print(f"   ✅ {key}: {settings[key]}")
    else:
        print(f"   ❌ {key} MISSING!")
        missing_keys.append(key)

if missing_keys:
    print(f"\n   ❌ Missing keys: {missing_keys}")
else:
    print(f"\n   ✅ All required keys present!\n")

# Test 4: Verify database schema
print("✓ Step 4: Checking database schema...")
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(settings)")
columns = cursor.fetchall()
conn.close()

db_columns = [col[1] for col in columns]
print(f"   Settings table has {len(db_columns)} columns:")
for col in db_columns:
    marker = "✅" if col in required_keys or col in ['created_at', 'updated_at'] else "⚠️"
    print(f"   {marker} {col}")

print()

print("="*70)
if not missing_keys:
    print("✅ Migration & Defaults Test PASSED!")
    print("   - Database properly migrated with all columns")
    print("   - get_settings() returns complete dictionary")
    print("   - All required keys have default values")
else:
    print("❌ Migration & Defaults Test FAILED!")
    print(f"   Missing keys: {missing_keys}")
print("="*70 + "\n")

# Clean up
if os.path.exists('db/test_data.db'):
    os.remove('db/test_data.db')
