"""
Authentication module for user login, signup, and session management.
Handles user authentication, profile creation, and family management.
"""

import sys
sys.path.insert(0, 'db')

from database import (
    create_user, get_user_by_username, authenticate_user,
    user_exists, create_family, get_family_by_code, add_user_to_family,
    get_family_members
)


def register_user(username: str, password: str, name: str,
                  gender: str, age: int, height: float,
                  current_weight: float, target_weight: float,
                  family_option: str, family_name: str = None,
                  family_code: str = None) -> tuple[bool, str, int]:
    """
    Register a new user with profile information.
    
    Args:
        username: Unique username
        password: User password
        name: Full name
        gender: Male/Female/Other
        age: Age in years
        height: Height in cm
        current_weight: Current weight in kg
        target_weight: Target weight in kg
        family_option: "create_new" or "join_existing"
        family_name: Name for new family (if creating)
        family_code: Code to join existing family
    
    Returns:
        (success: bool, message: str, user_id: int)
    """
    
    # Validate input
    if not username or len(username) < 3:
        return (False, "Username must be at least 3 characters", 0)
    
    if not password or len(password) < 6:
        return (False, "Password must be at least 6 characters", 0)
    
    if not name or len(name.strip()) == 0:
        return (False, "Name cannot be empty", 0)
    
    if age < 10 or age > 120:
        return (False, "Age must be between 10 and 120", 0)
    
    if height < 100 or height > 250:
        return (False, "Height must be between 100 and 250 cm", 0)
    
    if current_weight < 20 or current_weight > 500:
        return (False, "Current weight must be between 20 and 500 kg", 0)
    
    if target_weight < 20 or target_weight > 500:
        return (False, "Target weight must be between 20 and 500 kg", 0)
    
    # Check if username already exists
    if user_exists(username):
        return (False, "Username already exists. Please choose another.", 0)
    
    # Handle family
    family_id = None
    
    if family_option == "create_new":
        if not family_name or len(family_name.strip()) == 0:
            return (False, "Family name cannot be empty", 0)
        
        # We need a temporary user_id for creating family
        # Create the family after user is created, or use a default
        temp_family_name = family_name.strip()
    
    elif family_option == "join_existing":
        if not family_code or len(family_code.strip()) == 0:
            return (False, "Family code cannot be empty", 0)
        
        family = get_family_by_code(family_code.strip().upper())
        if not family:
            return (False, "Invalid family code. Please check and try again.", 0)
        
        family_id = family['family_id']
    
    # Create user
    user_id = create_user(
        username=username,
        password=password,
        name=name,
        family_id=family_id,
        gender=gender,
        age=age,
        height=height,
        current_weight=current_weight,
        target_weight=target_weight
    )
    
    if not user_id:
        return (False, "Error creating user. Please try again.", 0)
    
    # Create family if needed
    if family_option == "create_new":
        family_id = create_family(temp_family_name, user_id)
        if not family_id:
            return (False, "Error creating family. Please try again.", 0)
        
        # Update user's family_id
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET family_id = ? WHERE user_id = ?", (family_id, user_id))
        conn.commit()
        conn.close()
    
    return (True, "Account created successfully! Welcome to HealthTracker! 🎉", user_id)


def login_user(username: str, password: str) -> tuple[bool, str, int]:
    """
    Authenticate user with username and password.
    
    Args:
        username: Username
        password: Password
    
    Returns:
        (success: bool, message: str, user_id: int)
    """
    
    if not username or not password:
        return (False, "Username and password are required", 0)
    
    user_id = authenticate_user(username, password)
    
    if user_id:
        user = get_user_by_username(username)
        return (True, f"Welcome back, {user['name']}! 👋", user_id)
    else:
        return (False, "Invalid username or password", 0)


def get_user_info(user_id: int) -> dict:
    """Get detailed user information."""
    from database import get_user, get_settings, get_family
    
    user = get_user(user_id)
    settings = get_settings(user_id)
    family = None
    family_members = []
    
    if user and user['family_id']:
        family = get_family(user['family_id'])
        family_members = get_family_members(user['family_id'])
    
    return {
        'user': dict(user) if user else None,
        'settings': dict(settings) if settings else None,
        'family': dict(family) if family else None,
        'family_members': [dict(m) for m in family_members]
    }


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format and availability."""
    if not username:
        return (False, "Username cannot be empty")
    
    if len(username) < 3:
        return (False, "Username must be at least 3 characters")
    
    if len(username) > 20:
        return (False, "Username must be at most 20 characters")
    
    if not username.isalnum() and '_' not in username:
        return (False, "Username can only contain letters, numbers, and underscores")
    
    if user_exists(username):
        return (False, "Username already taken")
    
    return (True, "Username is available")


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if not password:
        return (False, "Password cannot be empty")
    
    if len(password) < 6:
        return (False, "Password must be at least 6 characters")
    
    if len(password) > 50:
        return (False, "Password must be at most 50 characters")
    
    return (True, "Password is valid")


if __name__ == "__main__":
    # Test the auth module
    print("Auth module loaded successfully!")
