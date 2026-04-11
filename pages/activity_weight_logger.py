"""
Activity & Weight Logging page for HealthTracker.
Allows users to log gym activities, walking, weight, and track calorie burn.
"""

import streamlit as st
import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from datetime import datetime, timedelta
from db.database import (
    get_user, get_daily_summary, update_daily_summary_activity,
    update_daily_summary_weight, update_daily_summary_cheat_day,
    create_daily_summary_if_needed, get_settings
)
from utils.calculations import (
    calculate_calories_burned_gym,
    calculate_calories_burned_walking,
    calculate_calorie_deficit
)
from utils.recommendations import generate_calculated_recommendations


def activity_weight_logger_page():
    """Render the activity and weight logging page."""
    st.title("🏋️ Activity & Weight Tracking")
    st.markdown("Log your exercises and daily weight")
    
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        st.error("Please login first")
        return
    
    user_id = st.session_state.user_id
    user = get_user(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    # Date selection
    col1, col2 = st.columns([2, 3])
    
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now().date(),
            key="activity_date_select"
        )
    
    # Create daily summary if it doesn't exist
    date_str = str(selected_date)
    create_daily_summary_if_needed(user_id, date_str)
    
    # Get current daily summary
    daily_summary = get_daily_summary(user_id, date_str)
    
    st.divider()
    
    # Tabs for different activity types
    tab1, tab2, tab3, tab4 = st.tabs(["💪 Gym Activity", "🚶 Walking/Running", "⚖️ Weight", "📊 Daily Summary"])
    
    with tab1:
        st.subheader("Gym Activity Logging")
        st.write("Log your gym workouts and calorie burn")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            gym_duration = st.number_input(
                "Duration (minutes)",
                min_value=5,
                max_value=480,
                value=30,
                step=5,
                key="gym_duration"
            )
        
        with col2:
            intensity = st.selectbox(
                "Intensity Level",
                ["Light", "Moderate", "Intense"],
                key="gym_intensity"
            )
        
        with col3:
            st.empty()
        
        # Calculate calories burned
        intensity_map = {"Light": 0.5, "Moderate": 1.0, "Intense": 1.5}
        intensity_multiplier = intensity_map[intensity]
        calories_gym = calculate_calories_burned_gym(gym_duration, intensity_multiplier)
        
        st.metric("Calories Burned (Gym)", f"{calories_gym:.0f} kcal")
        
        if st.button("💾 Save Gym Activity", width='stretch', key="save_gym_btn"):
            if update_daily_summary_activity(user_id, date_str, "gym", gym_duration, intensity, calories_gym):
                st.success(f"✅ Logged {gym_duration}min {intensity} intensity gym activity ({calories_gym:.0f} kcal)")
                st.rerun()
            else:
                st.error("❌ Failed to save gym activity")
        
        # Show today's gym activities
        if daily_summary:
            if (daily_summary.get('calories_gym') or 0) > 0:
                st.info(f"📈 **Today's Gym Total:** {daily_summary['calories_gym']:.0f} kcal burned")
    
    with tab2:
        st.subheader("Walking/Running Logging")
        st.write("Log walking or running distance and calorie burn")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            distance_km = st.number_input(
                "Distance (km)",
                min_value=0.1,
                max_value=100.0,
                value=5.0,
                step=0.1,
                key="walk_distance"
            )
        
        with col2:
            duration_minutes = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=480,
                value=60,
                step=5,
                key="walk_duration"
            )
        
        with col3:
            st.empty()
        
        # Calculate calories burned (using pace calculation)
        calories_walk = calculate_calories_burned_walking(distance_km, duration_minutes)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Distance", f"{distance_km:.1f} km")
        with col2:
            st.metric("Calories Burned", f"{calories_walk:.0f} kcal")
        
        pace_km_per_hour = (distance_km / duration_minutes) * 60 if duration_minutes > 0 else 0
        st.caption(f"⏱️ Pace: {pace_km_per_hour:.1f} km/h")
        
        if st.button("💾 Save Walking/Running", width='stretch', key="save_walk_btn"):
            if update_daily_summary_activity(user_id, date_str, "walk", distance_km, f"{pace_km_per_hour:.1f} km/h", calories_walk):
                st.success(f"✅ Logged {distance_km:.1f}km walk ({calories_walk:.0f} kcal)")
                st.rerun()
            else:
                st.error("❌ Failed to save walking activity")
        
        # Show today's walk activities
        if daily_summary:
            if (daily_summary.get('calories_walk') or 0) > 0:
                st.info(f"📈 **Today's Walking Total:** {daily_summary['calories_walk']:.0f} kcal burned")
    
    with tab3:
        st.subheader("⚖️ Weight Logging")
        st.write("Track your daily weight and set cheat day flag")
        
        col1, col2 = st.columns(2)
        
        with col1:
            daily_weight = st.number_input(
                "Weight (kg)",
                min_value=20.0,
                max_value=300.0,
                value=float(user['current_weight']),
                step=0.1,
                key="daily_weight_input"
            )
        
        with col2:
            is_cheat_day = st.checkbox(
                "🍕 Cheat Day",
                value=False,
                help="Mark if this was a cheat day with relaxed diet goals",
                key="cheat_day_checkbox"
            )
        
        # Show weight change
        if daily_summary and daily_summary.get('weight'):
            weight_change = daily_weight - daily_summary['weight']
            if weight_change < 0:
                st.metric("Weight Change", f"{weight_change:.1f} kg", delta=f"{weight_change:.1f} kg ✅")
            elif weight_change > 0:
                st.metric("Weight Change", f"{weight_change:.1f} kg", delta=f"{weight_change:.1f} kg ⚠️")
            else:
                st.metric("Weight Change", "0.0 kg", delta="No change")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Weight", width='stretch', key="save_weight_btn"):
                if update_daily_summary_weight(user_id, date_str, daily_weight):
                    st.success(f"✅ Logged weight: {daily_weight} kg")
                    st.rerun()
                else:
                    st.error("❌ Failed to save weight")
        
        with col2:
            if st.button("🍕 Save Cheat Day Flag", width='stretch', key="save_cheat_btn"):
                if update_daily_summary_cheat_day(user_id, date_str, 1 if is_cheat_day else 0):
                    status = "marked ✅" if is_cheat_day else "unmarked"
                    st.success(f"✅ Cheat day {status}")
                    st.rerun()
                else:
                    st.error("❌ Failed to save cheat day flag")
        
        # Show current day's weight
        if daily_summary and daily_summary.get('weight'):
            st.info(f"📊 **Today's Weight:** {daily_summary['weight']} kg")
    
    with tab4:
        st.subheader("📊 Daily Summary & Calorie Deficit")
        
        if not daily_summary:
            st.warning("No data for this date yet")
            return
        
        # Get user's computed recommendations from Recommendations tab
        # These are the same values displayed in Settings & Recommendations page
        with st.spinner("🔄 Loading your targets..."):
            calculated_rec = generate_calculated_recommendations(user_id)
        
        if not calculated_rec:
            st.error("Failed to compute recommendations")
            return
        
        # Extract target values from Recommendations tab
        daily_calorie_target = calculated_rec.get('daily_calories', 0)
        exercise_calories_target = calculated_rec.get('exercise_calories', 0)
        bmr = calculated_rec.get('bmr', 0)
        
        # Create columns for metrics - Row 1: Calorie Consumption
        col1, col2, col3, col4 = st.columns(4)
        
        calories_consumed = daily_summary.get('calories_consumed', 0)
        
        with col1:
            st.metric(
                "Calories Consumed",
                f"{calories_consumed:.0f} kcal",
                delta=f"{calories_consumed - daily_calorie_target:+.0f}",
                help="vs. Calorie Target"
            )
        
        with col2:
            st.metric(
                "Calorie Target",
                f"{daily_calorie_target:.0f} kcal",
                help="Daily calorie intake goal"
            )
        
        with col3:
            st.metric(
                "Gym Calories",
                f"{daily_summary.get('calories_gym', 0):.0f} kcal",
                delta="Burned",
                help="Calories burned from gym"
            )
        
        with col4:
            st.metric(
                "Walking Calories",
                f"{daily_summary.get('calories_walk', 0):.0f} kcal",
                delta="Burned",
                help="Calories burned from walking"
            )
        
        st.divider()
        
        # Row 2: Exercise and BMR (from Recommendations tab)
        col1, col2, col3, col4 = st.columns(4)
        
        calories_burned_total = (daily_summary.get('calories_gym', 0) + 
                                daily_summary.get('calories_walk', 0))
        
        with col1:
            st.metric("Exercise Target", f"{exercise_calories_target:.0f} kcal", help="From Recommendations tab")
        
        with col2:
            status = "✅" if calories_burned_total >= exercise_calories_target else "⚠️"
            st.metric("Exercise Actual", f"{calories_burned_total:.0f} kcal", delta=f"{calories_burned_total - exercise_calories_target:+.0f} {status}")
        
        with col3:
            st.metric("BMR", f"{bmr:.0f} kcal", help="From Recommendations tab")
        
        with col4:
            st.metric(
                "Walking Calories",
                f"{daily_summary.get('calories_walk', 0):.0f} kcal",
                delta="Burned",
                help="Calories burned from walking"
            )
        
        st.divider()
        
        # Row 3: Net Energy Balance - Target vs Actual with original signs
        col1, col2 = st.columns(2)
        
        # Calculate Net values using formula: Calories - Exercise Burn - BMR
        net_surplus_target = daily_calorie_target - exercise_calories_target - bmr
        net_surplus_actual = calories_consumed - calories_burned_total - bmr
        
        with col1:
            st.markdown("#### 🎯 Net Energy Balance - Target")
            if net_surplus_target < 0:
                st.metric(
                    "Target Deficit",
                    f"{net_surplus_target:.0f} kcal",
                    help="Negative = Deficit (weight loss)"
                )
            elif net_surplus_target > 0:
                st.metric(
                    "Target Surplus",
                    f"{net_surplus_target:+.0f} kcal",
                    help="Positive = Surplus (weight gain)"
                )
            else:
                st.metric("Target Balanced", "0 kcal", help="Maintenance")
            st.caption("Formula: Calories Target - Exercise Target - BMR")
        
        with col2:
            st.markdown("#### 📊 Net Energy Balance - Actual")
            if net_surplus_actual < 0:
                st.metric(
                    "Actual Deficit",
                    f"{net_surplus_actual:.0f} kcal",
                    delta=f"{net_surplus_actual - net_surplus_target:+.0f} ✅",
                    help="Negative = Deficit (weight loss)"
                )
            elif net_surplus_actual > 0:
                st.metric(
                    "Actual Surplus",
                    f"{net_surplus_actual:+.0f} kcal",
                    delta=f"{net_surplus_actual - net_surplus_target:+.0f} ⚠️",
                    help="Positive = Surplus (weight gain)"
                )
            else:
                st.metric(
                    "Balanced",
                    "0 kcal",
                    delta=f"{net_surplus_actual - net_surplus_target:+.0f}",
                    help="Maintenance"
                )
            st.caption("Formula: Calories Consumed - Exercise Actual - BMR")
        
        # Show weight if logged
        if daily_summary.get('weight'):
            st.divider()
            st.subheader("⚖️ Weight")
            st.metric("Weight", f"{daily_summary['weight']:.1f} kg")
        
        st.divider()
        
        # Cheat day indicator
        if daily_summary.get('is_cheat_day'):
            st.warning("🍕 **CHEAT DAY** - Goals are relaxed for today")
        
        # Water intake
        st.subheader("💧 Water Intake")
        st.metric("Water Consumed", f"{daily_summary.get('water_intake_liters', 0):.1f} L")
        
        # Macros
        st.subheader("🥗 Macronutrients")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Protein", f"{daily_summary.get('protein', 0):.0f}g")
        with col2:
            st.metric("Carbs", f"{daily_summary.get('carbs', 0):.0f}g")
        with col3:
            st.metric("Fat", f"{daily_summary.get('fat', 0):.0f}g")
        with col4:
            st.metric("Fiber", f"{daily_summary.get('fiber', 0):.0f}g")


if __name__ == "__main__":
    activity_weight_logger_page()
