# HealthTracker - Calorie & Water Intake Tracker

A comprehensive health tracking web application built with Streamlit for monitoring daily calorie intake, water consumption, weight, and activities.

## Features

- **User Management**
  - Secure login with password hashing (bcrypt)
  - Multi-user family support with family grouping
  - User profile creation with health metrics (age, height, weight, target weight)

- **Meal & Calorie Tracking**
  - Natural language meal logging (e.g., "1 bowl chicken biryani")
  - GPT-powered calorie calculation with macro breakdown (protein, carbs, fat, fiber)
  - Flexible meal types: Breakfast, Lunch, Dinner, Snack

- **Water Intake Tracking**
  - Quick add buttons for common water amounts (250ml, 500ml, 1L)
  - Custom water intake logging
  - Daily water goal tracking (default: 3L)
  - Hydration progress visualization

- **Activity & Weight Logging**
  - Walk distance/duration to calories burned conversion
  - Gym activity tracking with intensity levels
  - Daily weight logging and tracking
  - Cheat day flag for dietary flexibility

- **Analytics & Insights**
  - Interactive graphs for calorie trends, weight progress, macros breakdown
  - Family comparison dashboard (side-by-side progress tracking)
  - Daily, weekly, and monthly aggregations
  - Hydration status indicators

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** SQLite
- **Calorie Calculation:** OpenAI GPT API
- **Visualization:** Plotly
- **Authentication:** bcrypt
- **Deployment:** Streamlit Cloud

## Project Structure

```
HealthTracker/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── .gitignore             # Git ignore rules
├── .streamlit/
│   ├── config.toml        # Streamlit configuration
│   └── secrets.toml       # Secrets (for deployment)
├── db/
│   ├── __init__.py
│   ├── database.py        # SQLite operations (Phase 2)
│   └── data.db            # SQLite database (auto-created)
├── utils/
│   ├── __init__.py
│   ├── auth.py            # Authentication & user management (Phase 3)
│   ├── gpt_utils.py       # GPT API integration (Phase 4)
│   ├── calculations.py    # Calorie & health calculations (Phase 6)
│   └── validators.py      # Input validation utilities
└── pages/
    ├── __init__.py
    ├── home.py            # Dashboard (Phase 7)
    ├── profile.py         # User profile (Phase 3)
    ├── meal_logger.py     # Meal logging UI (Phase 5)
    ├── water_tracker.py   # Water intake UI (Phase 5)
    ├── analytics.py       # Graphs & analytics (Phase 7)
    └── family_dashboard.py # Family tracking (Phase 8)
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone/Create project directory:**
   ```bash
   cd c:\Swapnil\GenerativeAI\HealthTracker
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or: source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Edit `.env` file
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-your-key-here
     ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

6. **Access the app:**
   - Open browser to `http://localhost:8501`

## Development Phases

- **Phase 1:** ✅ Project Setup & Infrastructure
- **Phase 2:** Database Layer (SQLite schema & operations)
- **Phase 3:** Authentication & User Profile
- **Phase 4:** GPT Integration for Calorie Calculation
- **Phase 5:** Meal & Water Logging Features
- **Phase 6:** Activity & Weight Logging
- **Phase 7:** Analytics & Graphs
- **Phase 8:** UI Polish & Family Features
- **Phase 9:** Testing & Bug Fixes
- **Phase 10:** Deployment to Streamlit Cloud

## Usage

1. **First Time Users:**
   - Click "First time?" to create a profile
   - Enter name, gender, age, height, current weight, target weight
   - Create or join family group
   - Set daily calorie deficit and water goal

2. **Daily Tracking:**
   - Log meals in natural language (Streamlit calculates calories via GPT)
   - Log water intake throughout the day
   - Record gym/walk activities
   - Log daily weight (optional)
   - Mark days as "cheat day" if desired

3. **Analytics:**
   - View daily/weekly/monthly progress charts
   - Compare family members' progress
   - Track hydration and calorie trends
   - Export data to CSV

## Configuration

Edit `config.py` to customize:
- Default calorie deficit constant (kcal/day)
- Default water goal (liters/day)
- Calorie burn rates for different activities
- OpenAI model (gpt-3.5-turbo, gpt-4, etc.)

## Database Schema (Phase 2)

### users
```
user_id, family_id, username, password_hash, name, gender, age, height, 
target_weight, created_at
```

### families
```
family_id, family_name, family_code, created_by, created_at
```

### nutrition_log
```
id, user_id, date, meal_type, meal_description, calories, protein, carbs, 
fat, fiber, gpt_raw_response, created_at
```

### daily_summary
```
id, user_id, date, calories_consumed, protein, carbs, fat, fiber, 
calories_walk, calories_gym, calories_burned, calorie_deficit, 
water_intake_liters, weight, is_cheat_day, created_at, updated_at
```

### settings
```
user_id, calorie_deficit_constant, daily_water_goal_liters, 
created_at, updated_at
```

### water_log
```
id, user_id, date, water_intake_liters, time, timestamp
```

## Troubleshooting

- **GPT API Error:** Check OpenAI API key in `.env`
- **Database Error:** Delete `db/data.db` to reset database
- **Import Error:** Run `pip install -r requirements.txt`
- **Streamlit Cache Issues:** Run with `streamlit run app.py --logger.level=debug`

## Future Enhancements

- Export data to CSV/PDF reports
- Meal recommendations based on history
- Nutrition goals customization (high-protein, keto, etc.)
- Mobile app version
- Email/SMS notifications

## License

This project is for personal use.

---

**Next Phase:** Phase 2 - Database Layer Setup
