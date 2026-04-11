"""
Database module for HealthTracker - SQLite operations and schema management.
Handles all database interactions for users, families, meals, nutrition tracking, and activities.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import hashlib
import secrets

DB_PATH = "db/data.db"


def get_db_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with all required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Families table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS families (
                family_id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_name TEXT NOT NULL,
                family_code TEXT UNIQUE NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        """)

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                height REAL,
                current_weight REAL,
                target_weight REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES families(family_id)
            )
        """)

        # Nutrition log table (raw meal entries)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                meal_type TEXT NOT NULL,
                meal_description TEXT NOT NULL,
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                fiber REAL,
                gpt_raw_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Water log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                water_intake_liters REAL NOT NULL,
                time TIME,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Daily summary table (aggregated daily data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL UNIQUE,
                calories_consumed REAL DEFAULT 0,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                fiber REAL DEFAULT 0,
                calories_walk REAL DEFAULT 0,
                calories_gym REAL DEFAULT 0,
                calories_burned REAL DEFAULT 0,
                exercise_calories_goal REAL DEFAULT 0,
                calorie_deficit REAL DEFAULT 0,
                water_intake_liters REAL DEFAULT 0,
                weight REAL,
                is_cheat_day INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, date)
            )
        """)

        # Settings table (user-specific settings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,
                calorie_deficit_constant REAL DEFAULT 500,
                daily_water_goal_liters REAL DEFAULT 3.0,
                activity_level TEXT DEFAULT 'moderate',
                diet_preference TEXT DEFAULT 'balanced',
                goal_type TEXT DEFAULT 'weight_loss',
                target_loss_per_week REAL DEFAULT 0.5,
                recommended_daily_calories REAL DEFAULT 0,
                recommended_protein REAL DEFAULT 0,
                recommended_carbs REAL DEFAULT 0,
                recommended_fat REAL DEFAULT 0,
                exercise_calories_target REAL DEFAULT 0,
                use_recommendations INTEGER DEFAULT 1,
                custom_calorie_goal REAL DEFAULT 0,
                custom_protein_goal REAL DEFAULT 0,
                custom_carbs_goal REAL DEFAULT 0,
                custom_fat_goal REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        conn.commit()
        
        # Run migrations for existing databases
        migrate_db()
        
        print("✅ Database initialized successfully!")
        return True

    except sqlite3.Error as e:
        print(f"❌ Database initialization error: {e}")
        return False
    finally:
        conn.close()


def migrate_db():
    """Apply any necessary migrations to existing databases."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        if not cursor.fetchone():
            return  # Table doesn't exist yet, will be created
        
        # Get existing columns in settings table
        cursor.execute("PRAGMA table_info(settings)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Define columns that should exist
        expected_columns = {
            'activity_level': "TEXT DEFAULT 'moderate'",
            'diet_preference': "TEXT DEFAULT 'balanced'",
            'goal_type': "TEXT DEFAULT 'weight_loss'",
            'target_loss_per_week': "REAL DEFAULT 0.5",
            'recommended_daily_calories': "REAL DEFAULT 0",
            'recommended_protein': "REAL DEFAULT 0",
            'recommended_carbs': "REAL DEFAULT 0",
            'recommended_fat': "REAL DEFAULT 0",
            'exercise_calories_target': "REAL DEFAULT 0",
            'use_recommendations': "INTEGER DEFAULT 1",
            'custom_calorie_goal': "REAL DEFAULT 0",
            'custom_protein_goal': "REAL DEFAULT 0",
            'custom_carbs_goal': "REAL DEFAULT 0",
            'custom_fat_goal': "REAL DEFAULT 0",
        }
        
        # Add missing columns to settings table
        for col_name, col_def in expected_columns.items():
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE settings ADD COLUMN {col_name} {col_def}")
                except sqlite3.OperationalError as e:
                    pass  # Column may already exist, ignore
        
        # Check if daily_summary table exists and add missing columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_summary'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(daily_summary)")
            daily_summary_columns = [col[1] for col in cursor.fetchall()]
            
            # Add exercise_calories_goal if missing
            if 'exercise_calories_goal' not in daily_summary_columns:
                try:
                    cursor.execute("ALTER TABLE daily_summary ADD COLUMN exercise_calories_goal REAL DEFAULT 0")
                except sqlite3.OperationalError as e:
                    pass  # Column may already exist, ignore
        
        conn.commit()
    except Exception as e:
        # Log but don't fail - migration errors shouldn't break the app
        pass
    finally:
        if conn:
            conn.close()


# ==================== USER MANAGEMENT ====================

def create_user(username: str, password: str, name: str, family_id: Optional[int] = None,
                gender: Optional[str] = None, age: Optional[int] = None,
                height: Optional[float] = None, current_weight: Optional[float] = None,
                target_weight: Optional[float] = None) -> Optional[int]:
    """Create a new user account. Returns user_id if successful, None otherwise."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)

        cursor.execute("""
            INSERT INTO users (family_id, username, password_hash, name, gender, age, height, current_weight, target_weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (family_id, username, password_hash, name, gender, age, height, current_weight, target_weight))

        user_id = cursor.lastrowid

        # Create default settings for user
        cursor.execute("""
            INSERT INTO settings (user_id, calorie_deficit_constant, daily_water_goal_liters)
            VALUES (?, 500, 3.0)
        """, (user_id,))

        conn.commit()
        return user_id

    except sqlite3.Error as e:
        print(f"❌ Error creating user: {e}")
        return None
    finally:
        conn.close()


def get_user(user_id: int) -> Optional[Dict]:
    """Get user details by user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user details by username."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> Optional[int]:
    """Authenticate user and return user_id if credentials are correct, None otherwise."""
    user = get_user_by_username(username)

    if user and verify_password(password, user['password_hash']):
        return user['user_id']
    return None


def user_exists(username: str) -> bool:
    """Check if a username already exists."""
    return get_user_by_username(username) is not None


def update_user_profile(user_id: int, **kwargs) -> bool:
    """Update user profile information."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        allowed_fields = ['name', 'gender', 'age', 'height', 'current_weight', 'target_weight']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return True

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [datetime.now(), user_id]

        cursor.execute(f"""
            UPDATE users
            SET {set_clause}, updated_at = ?
            WHERE user_id = ?
        """, values)

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"❌ Error updating user profile: {e}")
        return False
    finally:
        conn.close()


# ==================== FAMILY MANAGEMENT ====================

def create_family(family_name: str, created_by: int) -> Optional[int]:
    """Create a new family group. Returns family_id if successful, None otherwise."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        family_code = generate_family_code()

        cursor.execute("""
            INSERT INTO families (family_name, family_code, created_by)
            VALUES (?, ?, ?)
        """, (family_name, family_code, created_by))

        family_id = cursor.lastrowid
        conn.commit()
        return family_id

    except sqlite3.Error as e:
        print(f"❌ Error creating family: {e}")
        return None
    finally:
        conn.close()


def get_family(family_id: int) -> Optional[Dict]:
    """Get family details by family_id."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM families WHERE family_id = ?", (family_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_family_by_code(family_code: str) -> Optional[Dict]:
    """Get family details by family code."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM families WHERE family_code = ?", (family_code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_family_members(family_id: int) -> List[Dict]:
    """Get all members of a family."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE family_id = ? ORDER BY created_at", (family_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def add_user_to_family(user_id: int, family_id: int) -> bool:
    """Add an existing user to a family."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE users SET family_id = ? WHERE user_id = ?", (family_id, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"❌ Error adding user to family: {e}")
        return False
    finally:
        conn.close()


# ==================== MEAL & NUTRITION LOGGING ====================

def log_meal(user_id: int, date: str, meal_type: str, meal_description: str,
             calories: Optional[float] = None, protein: Optional[float] = None,
             carbs: Optional[float] = None, fat: Optional[float] = None,
             fiber: Optional[float] = None, gpt_raw_response: Optional[str] = None) -> Optional[int]:
    """Log a meal entry. Returns meal_id if successful, None otherwise."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO nutrition_log 
            (user_id, date, meal_type, meal_description, calories, protein, carbs, fat, fiber, gpt_raw_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, meal_type, meal_description, calories, protein, carbs, fat, fiber, gpt_raw_response))

        meal_id = cursor.lastrowid
        conn.commit()
        return meal_id

    except sqlite3.Error as e:
        print(f"❌ Error logging meal: {e}")
        return None
    finally:
        conn.close()


def get_meals_by_date(user_id: int, date: str) -> List[Dict]:
    """Get all meals logged for a specific user on a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM nutrition_log
            WHERE user_id = ? AND date = ?
            ORDER BY created_at
        """, (user_id, date))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_meals_by_date_range(user_id: int, start_date: str, end_date: str) -> List[Dict]:
    """Get all meals logged for a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM nutrition_log
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date, created_at
        """, (user_id, start_date, end_date))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_meal(meal_id: int) -> bool:
    """Delete a meal entry."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM nutrition_log WHERE id = ?", (meal_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"❌ Error deleting meal: {e}")
        return False
    finally:
        conn.close()


# ==================== WATER INTAKE LOGGING ====================

def log_water(user_id: int, date: str, water_liters: float, time: Optional[str] = None) -> Optional[int]:
    """Log water intake. Returns water_log_id if successful, None otherwise."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO water_log (user_id, date, water_intake_liters, time)
            VALUES (?, ?, ?, ?)
        """, (user_id, date, water_liters, time))

        water_id = cursor.lastrowid
        conn.commit()
        return water_id

    except sqlite3.Error as e:
        print(f"❌ Error logging water: {e}")
        return None
    finally:
        conn.close()


def get_water_log_by_date(user_id: int, date: str) -> List[Dict]:
    """Get all water intake entries for a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM water_log
            WHERE user_id = ? AND date = ?
            ORDER BY time
        """, (user_id, date))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_total_water_by_date(user_id: int, date: str) -> float:
    """Get total water intake for a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT SUM(water_intake_liters) as total
            FROM water_log
            WHERE user_id = ? AND date = ?
        """, (user_id, date))

        row = cursor.fetchone()
        return row['total'] or 0.0
    finally:
        conn.close()


# ==================== DAILY SUMMARY ====================

def save_daily_summary(user_id: int, date: str, calories_consumed: float = 0,
                      protein: float = 0, carbs: float = 0, fat: float = 0, fiber: float = 0,
                      calories_walk: float = 0, calories_gym: float = 0, calories_burned: float = 0,
                      calorie_deficit: float = 0, water_intake: float = 0,
                      weight: Optional[float] = None, is_cheat_day: int = 0) -> bool:
    """Save or update daily summary for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR REPLACE INTO daily_summary
            (user_id, date, calories_consumed, protein, carbs, fat, fiber,
             calories_walk, calories_gym, calories_burned, calorie_deficit, water_intake_liters,
             weight, is_cheat_day, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, calories_consumed, protein, carbs, fat, fiber,
              calories_walk, calories_gym, calories_burned, calorie_deficit, water_intake,
              weight, is_cheat_day, datetime.now()))

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"❌ Error saving daily summary: {e}")
        return False
    finally:
        conn.close()


def get_daily_summary(user_id: int, date: str) -> Optional[Dict]:
    """Get daily summary for a user on a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM daily_summary
            WHERE user_id = ? AND date = ?
        """, (user_id, date))

        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_daily_summaries_range(user_id: int, start_date: str, end_date: str) -> List[Dict]:
    """Get daily summaries for a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM daily_summary
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date
        """, (user_id, start_date, end_date))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_daily_summary_weight(user_id: int, date: str, weight: float) -> bool:
    """Update weight in daily summary."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE daily_summary
            SET weight = ?, updated_at = ?
            WHERE user_id = ? AND date = ?
        """, (weight, datetime.now(), user_id, date))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"❌ Error updating weight: {e}")
        return False
    finally:
        conn.close()


def update_daily_summary_cheat_day(user_id: int, date: str, is_cheat_day: int) -> bool:
    """Update cheat day flag in daily summary."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE daily_summary
            SET is_cheat_day = ?, updated_at = ?
            WHERE user_id = ? AND date = ?
        """, (is_cheat_day, datetime.now(), user_id, date))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"❌ Error updating cheat day flag: {e}")
        return False
    finally:
        conn.close()


def create_daily_summary_if_needed(user_id: int, date: str) -> bool:
    """
    Create a daily summary row for the user if it doesn't exist.
    Also populates exercise_calories_goal from settings.
    
    Args:
        user_id: User ID
        date: Date string (YYYY-MM-DD)
    
    Returns:
        True if created or already exists, False on error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if row exists
        cursor.execute(
            "SELECT id FROM daily_summary WHERE user_id = ? AND date = ?",
            (user_id, date)
        )
        
        if not cursor.fetchone():
            # Get exercise_calories_goal from settings
            cursor.execute(
                "SELECT exercise_calories_target FROM settings WHERE user_id = ?",
                (user_id,)
            )
            settings_row = cursor.fetchone()
            exercise_goal = settings_row[0] if settings_row else 0
            
            # Row doesn't exist, create it
            cursor.execute("""
                INSERT INTO daily_summary 
                (user_id, date, calories_consumed, protein, carbs, fat, fiber,
                 calories_walk, calories_gym, calories_burned, exercise_calories_goal,
                 calorie_deficit, water_intake_liters, is_cheat_day, created_at, updated_at)
                VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, ?, 0, 0, 0, ?, ?)
            """, (user_id, date, exercise_goal, datetime.now(), datetime.now()))
            conn.commit()
        
        return True
    except sqlite3.Error as e:
        print(f"❌ Error creating daily summary: {e}")
        return False
    finally:
        conn.close()


def update_daily_summary_activity(user_id: int, date: str, activity_type: str,
                                  duration_or_distance: float, pace_or_intensity: str,
                                  calories_burned: float) -> bool:
    """
    Update activity (gym or walking) in daily summary.
    
    Args:
        user_id: User ID
        date: Date string (YYYY-MM-DD)
        activity_type: "gym" or "walk"
        duration_or_distance: Duration in minutes for gym, distance in km for walk
        pace_or_intensity: Pace for walking, intensity level for gym
        calories_burned: Calories burned (already calculated)
    
    Returns:
        True if successful, False on error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if activity_type == "gym":
            cursor.execute("""
                UPDATE daily_summary
                SET calories_gym = calories_gym + ?,
                    updated_at = ?
                WHERE user_id = ? AND date = ?
            """, (calories_burned, datetime.now(), user_id, date))
        
        elif activity_type == "walk":
            cursor.execute("""
                UPDATE daily_summary
                SET calories_walk = calories_walk + ?,
                    updated_at = ?
                WHERE user_id = ? AND date = ?
            """, (calories_burned, datetime.now(), user_id, date))
        
        conn.commit()
        return True
    
    except sqlite3.Error as e:
        print(f"❌ Error updating activity: {e}")
        return False
    finally:
        conn.close()


# ==================== SETTINGS ====================

def get_settings(user_id: int) -> Optional[Dict]:
    """Get user settings with defaults for all expected fields."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Default values for all settings
    defaults = {
        'user_id': user_id,
        'calorie_deficit_constant': 500,
        'daily_water_goal_liters': 3.0,
        'activity_level': 'moderate',
        'diet_preference': 'balanced',
        'goal_type': 'weight_loss',
        'target_loss_per_week': 0.5,
        'recommended_daily_calories': 0,
        'recommended_protein': 0,
        'recommended_carbs': 0,
        'recommended_fat': 0,
        'use_recommendations': 1,
        'custom_calorie_goal': 0,
        'custom_protein_goal': 0,
        'custom_carbs_goal': 0,
        'custom_fat_goal': 0,
    }

    try:
        cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            # Merge database values with defaults
            settings = defaults.copy()
            settings.update(dict(row))
            return settings
        else:
            # No settings yet, return defaults
            return defaults
    finally:
        conn.close()


def update_settings(user_id: int, calorie_deficit: Optional[float] = None,
                   water_goal: Optional[float] = None) -> bool:
    """Update user settings."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if calorie_deficit is not None:
            cursor.execute("""
                UPDATE settings
                SET calorie_deficit_constant = ?, updated_at = ?
                WHERE user_id = ?
            """, (calorie_deficit, datetime.now(), user_id))

        if water_goal is not None:
            cursor.execute("""
                UPDATE settings
                SET daily_water_goal_liters = ?, updated_at = ?
                WHERE user_id = ?
            """, (water_goal, datetime.now(), user_id))

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"❌ Error updating settings: {e}")
        return False
    finally:
        conn.close()


# ==================== PASSWORD HASHING ====================

def hash_password(password: str) -> str:
    """Hash a password using SHA256 with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, pwd_hash = password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == pwd_hash
    except:
        return False


# ==================== UTILITIES ====================

def generate_family_code() -> str:
    """Generate a unique 6-character family code."""
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(6))


def delete_all_data():
    """Delete all data from database (for testing/reset only)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM water_log")
        cursor.execute("DELETE FROM nutrition_log")
        cursor.execute("DELETE FROM daily_summary")
        cursor.execute("DELETE FROM settings")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM families")
        conn.commit()
        print("✅ All data deleted successfully!")
        return True
    except sqlite3.Error as e:
        print(f"❌ Error deleting data: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    # Initialize database when module is run directly
    init_db()
    print("Database module loaded successfully!")
