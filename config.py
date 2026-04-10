"""Configuration and constants for HealthTracker app."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"

# Database Configuration
DB_PATH = "db/data.db"

# Default Settings
DEFAULT_CALORIE_DEFICIT = 500  # kcal/day
DEFAULT_WATER_GOAL = 3.0  # liters per day

# Calorie Calculation Constants
CALORIES_PER_KM_WALKING = 80  # kcal/km
CALORIES_PER_MIN_WALKING = 5  # kcal/min
CALORIES_PER_MIN_GYM_LOW = 5  # kcal/min (low intensity)
CALORIES_PER_MIN_GYM_MEDIUM = 8  # kcal/min (medium intensity)
CALORIES_PER_MIN_GYM_HIGH = 12  # kcal/min (high intensity)

# App Settings
APP_NAME = "HealthTracker"
DEBUG = os.getenv("DEBUG", "False") == "True"
