## Fix for KeyError: 'activity_level'

### Problem
Existing users created before Phase 6A were missing the new recommendation columns in the settings table, causing `KeyError` when accessing fields like `activity_level`.

### Root Cause
The database schema was updated with 13 new columns, but existing databases didn't have these columns. When `get_settings()` queried the database and returned the old row dict, it was missing the expected keys.

### Solution Implemented

#### 1. **Database Migration (db/database.py)**
Added `migrate_db()` function that:
- Checks existing columns in the settings table
- Adds any missing recommendation columns automatically
- Runs on every app startup via `init_db()`
- Handles errors gracefully

**Missing columns that will be added:**
- `activity_level` (TEXT DEFAULT 'moderate')
- `diet_preference` (TEXT DEFAULT 'balanced')
- `goal_type` (TEXT DEFAULT 'weight_loss')
- `target_loss_per_week` (REAL DEFAULT 0.5)
- `recommended_daily_calories` (REAL DEFAULT 0)
- `recommended_protein` (REAL DEFAULT 0)
- `recommended_carbs` (REAL DEFAULT 0)
- `recommended_fat` (REAL DEFAULT 0)
- `use_recommendations` (INTEGER DEFAULT 1)
- `custom_calorie_goal` (REAL DEFAULT 0)
- `custom_protein_goal` (REAL DEFAULT 0)
- `custom_carbs_goal` (REAL DEFAULT 0)
- `custom_fat_goal` (REAL DEFAULT 0)

#### 2. **Enhanced get_settings() Function (db/database.py)**
Updated to always return a complete dictionary:
- Defines defaults for all 15+ expected fields
- Merges database values with defaults
- Returns defaults if no settings exist yet
- Prevents KeyErrors even if columns are missing

#### 3. **Defensive Code in settings_recommendations.py**
Changed direct bracket access to safe `.get()` method:
```python
# Before (unsafe):
current_activity = settings['activity_level']

# After (safe):
current_activity = settings.get('activity_level', 'moderate')
```

#### 4. **Defensive Code in get_active_recommendations() (utils/recommendations.py)**
Updated all settings access to use `.get()` with defaults:
```python
if settings.get('use_recommendations', 1):
    return {
        'daily_calories': settings.get('recommended_daily_calories', 0),
        'protein_grams': settings.get('recommended_protein', 0),
        ...
    }
```

### How It Works

1. **On App Startup:**
   - `app.py` calls `init_db()`
   - `init_db()` creates/validates all tables
   - `init_db()` calls `migrate_db()`
   - `migrate_db()` adds missing columns to existing settings tables

2. **When User Accesses Settings:**
   - `get_settings(user_id)` is called
   - Queries database for user's settings row
   - Merges result with defaults
   - Returns complete dict with all expected keys
   - No more KeyError!

3. **Code Safety:**
   - All settings access uses `.get()` with fallback values
   - Even if a column is somehow missing, code won't crash
   - Defaults are applied automatically

### Testing
Run this to verify the fix works:
```bash
streamlit run app.py
```

Then:
1. Create a new account → Settings will have all default values
2. Login with old account → Migration adds missing columns, get_settings returns defaults

### Backward Compatibility
✅ All existing user data is preserved
✅ Existing users can still login and use all features
✅ No data loss or reset required
✅ Seamless upgrade path

### Files Modified
1. `db/database.py` - Added migrate_db(), enhanced get_settings()
2. `utils/recommendations.py` - Safe settings access with .get()
3. `pages/settings_recommendations.py` - Safe settings access with .get()
