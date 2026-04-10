"""
Settings & Recommendations page for HealthTracker.
Allows users to view and customize calorie and macro recommendations.
"""

import streamlit as st
import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from database import get_user, get_settings, update_settings
from recommendations import (
    generate_calculated_recommendations,
    generate_gpt_recommendations,
    save_recommendations,
    save_custom_recommendations,
    update_user_profile_preferences,
    get_active_recommendations
)
from calculations import calculate_macronutrient_percentages


def settings_recommendations_page():
    """Render the settings and recommendations page."""
    st.title("⚙️ Settings & Recommendations")
    st.markdown("Personalize your calorie and macro targets")
    
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        st.error("Please login first")
        return
    
    user_id = st.session_state.user_id
    user = get_user(user_id)
    settings = get_settings(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["👤 Profile & Goals", "🎯 Recommendations", "💾 Custom Goals"])
    
    with tab1:
        st.subheader("Your Profile & Goals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Current Weight", f"{user['current_weight']} kg")
            st.metric("Target Weight", f"{user['target_weight']} kg")
            weight_to_lose = user['current_weight'] - user['target_weight']
            st.metric("Weight to Lose", f"{weight_to_lose} kg")
        
        with col2:
            st.metric("Age", f"{user['age']} years")
            st.metric("Height", f"{user['height']} cm")
            st.metric("Gender", user['gender'])
        
        st.divider()
        
        st.subheader("Preferences for Recommendations")
        
        col1, col2, col3 = st.columns(3)
        
        current_activity = settings.get('activity_level', 'moderate') if settings else 'moderate'
        current_diet = settings.get('diet_preference', 'balanced') if settings else 'balanced'
        current_target_loss = settings.get('target_loss_per_week', 0.5) if settings else 0.5
        
        with col1:
            activity_level = st.selectbox(
                "Activity Level",
                ["sedentary", "light", "moderate", "very_active", "extremely_active"],
                index=["sedentary", "light", "moderate", "very_active", "extremely_active"].index(current_activity),
                help="How much do you exercise per week?",
                key="activity_select"
            )
        
        with col2:
            diet_preference = st.selectbox(
                "Diet Preference",
                ["balanced", "high_protein", "low_carb", "vegetarian"],
                index=["balanced", "high_protein", "low_carb", "vegetarian"].index(current_diet),
                help="Your preferred macro distribution",
                key="diet_select"
            )
        
        with col3:
            target_loss = st.selectbox(
                "Weekly Weight Loss Target",
                [0.25, 0.5, 0.75, 1.0],
                index=[0.25, 0.5, 0.75, 1.0].index(current_target_loss),
                help="Recommended: 0.5-1.0 kg/week for sustainable loss",
                key="loss_target_select"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"📊 **Activity:** {activity_level.replace('_', ' ').title()}")
            st.caption("Affects daily calorie burn calculation")
        
        with col2:
            st.info(f"🍽️ **Diet:** {diet_preference.replace('_', ' ').title()}")
            st.caption("Determines macro ratios")
        
        with col3:
            st.info(f"📉 **Target:** {target_loss} kg/week")
            st.caption(f"~{target_loss * 4.33:.1f} kg/month")
        
        if st.button("💾 Save Preferences", use_container_width=True, key="save_prefs_btn"):
            if update_user_profile_preferences(
                user_id,
                activity_level=activity_level,
                diet_preference=diet_preference,
                target_loss_per_week=target_loss
            ):
                st.success("✅ Preferences saved!")
                st.rerun()
            else:
                st.error("❌ Failed to save preferences")
    
    with tab2:
        st.subheader("🎯 Your Daily Targets")
        
        # Get calculated recommendations
        with st.spinner("🔄 Calculating personalized recommendations..."):
            calculated_rec = generate_calculated_recommendations(user_id)
        
        if not calculated_rec:
            st.error("Failed to generate recommendations")
            return
        
        # Display calculated recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Calculated Recommendations")
            st.metric("Daily Calories", f"{calculated_rec['daily_calories']:.0f} kcal")
            st.metric("Protein", f"{calculated_rec['protein_grams']:.0f}g")
            st.metric("Carbs", f"{calculated_rec['carbs_grams']:.0f}g")
            st.metric("Fat", f"{calculated_rec['fat_grams']:.0f}g")
            st.metric("Daily Deficit", f"{calculated_rec['calorie_deficit']:.0f} kcal")
            
            st.divider()
            st.caption(f"**BMR:** {calculated_rec['bmr']:.0f} kcal/day")
            st.caption(f"**TDEE:** {calculated_rec['tdee']:.0f} kcal/day ({current_activity})")
        
        with col2:
            st.markdown("### 💡 Insights")
            st.info(f"**Goal:** Lose {weight_to_lose}kg at {current_target_loss}kg/week")
            st.success(f"**Timeline:** ~{weight_to_lose / current_target_loss:.0f} weeks to reach target")
            
            st.divider()
            st.markdown("**💬 Tips:**")
            for i, tip in enumerate(calculated_rec['tips'], 1):
                st.markdown(f"{i}. {tip}")
        
        st.divider()
        
        # GPT Recommendations option
        st.subheader("🤖 AI-Powered Recommendations (GPT)")
        st.write("Get personalized recommendations from GPT based on your profile")
        
        if st.button("✨ Generate GPT Recommendations", use_container_width=True, key="gpt_rec_btn"):
            with st.spinner("🤖 Getting GPT recommendations..."):
                gpt_rec = generate_gpt_recommendations(user_id)
            
            if gpt_rec:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🤖 GPT Recommendations")
                    st.metric("Daily Calories", f"{gpt_rec['daily_calories']:.0f} kcal")
                    st.metric("Protein", f"{gpt_rec['protein_grams']:.0f}g")
                    st.metric("Carbs", f"{gpt_rec['carbs_grams']:.0f}g")
                    st.metric("Fat", f"{gpt_rec['fat_grams']:.0f}g")
                    st.metric("Weekly Loss", f"{gpt_rec['weekly_weight_loss']:.2f} kg")
                
                with col2:
                    st.markdown("### 📝 AI Reasoning")
                    st.info(gpt_rec['reasoning'])
                    st.markdown("**AI Tips:**")
                    for i, tip in enumerate(gpt_rec['tips'], 1):
                        st.markdown(f"{i}. {tip}")
                
                st.divider()
                
                if st.button("💾 Use GPT Recommendations", use_container_width=True, key="use_gpt_rec_btn"):
                    if save_recommendations(user_id, gpt_rec, use_gpt=True):
                        st.success("✅ GPT recommendations activated!")
                        st.rerun()
            else:
                st.error("❌ Failed to get GPT recommendations. Check your API key.")
        
        st.divider()
        
        # Use calculated recommendations
        if st.button("✅ Use Calculated Recommendations", use_container_width=True, key="use_calc_rec_btn"):
            if save_recommendations(user_id, calculated_rec, use_gpt=False):
                st.success("✅ Calculated recommendations activated!")
                st.rerun()
    
    with tab3:
        st.subheader("🎯 Customize Your Goals")
        st.write("Override the recommendations with your custom targets")
        
        # Get current active recommendations as defaults
        active_rec = get_active_recommendations(user_id)
        
        # Use defaults if active_rec values are 0 (not set yet)
        default_calories = active_rec['daily_calories'] if active_rec and active_rec['daily_calories'] > 0 else 1800
        default_protein = active_rec['protein_grams'] if active_rec and active_rec['protein_grams'] > 0 else 120
        default_carbs = active_rec['carbs_grams'] if active_rec and active_rec['carbs_grams'] > 0 else 180
        default_fat = active_rec['fat_grams'] if active_rec and active_rec['fat_grams'] > 0 else 60
        default_deficit = active_rec['calorie_deficit'] if active_rec and active_rec['calorie_deficit'] > 0 else 500
        
        col1, col2 = st.columns(2)
        
        with col1:
            custom_calories = st.number_input(
                "Daily Calorie Goal (kcal)",
                min_value=800.0,
                max_value=5000.0,
                value=float(default_calories),
                step=50.0,
                key="custom_cal_input"
            )
            
            custom_protein = st.number_input(
                "Daily Protein Goal (g)",
                min_value=20.0,
                max_value=300.0,
                value=float(default_protein),
                step=5.0,
                key="custom_prot_input"
            )
        
        with col2:
            custom_carbs = st.number_input(
                "Daily Carbs Goal (g)",
                min_value=50.0,
                max_value=400.0,
                value=float(default_carbs),
                step=10.0,
                key="custom_carbs_input"
            )
            
            custom_fat = st.number_input(
                "Daily Fat Goal (g)",
                min_value=20.0,
                max_value=150.0,
                value=float(default_fat),
                step=5.0,
                key="custom_fat_input"
            )
        
        custom_deficit = st.number_input(
            "Calorie Deficit Constant (kcal/day)",
            min_value=100.0,
            max_value=1500.0,
            value=float(default_deficit),
            step=50.0,
            help="Daily deficit target for weight loss calculation",
            key="custom_deficit_input"
        )
        
        st.divider()
        
        # Calculate macro breakdown
        macros = calculate_macronutrient_percentages(custom_protein, custom_carbs, custom_fat)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Protein %", f"{macros['protein_percentage']:.1f}%")
        col2.metric("Carbs %", f"{macros['carbs_percentage']:.1f}%")
        col3.metric("Fat %", f"{macros['fat_percentage']:.1f}%")
        
        st.info(f"**Total Macros Calories:** {macros['total_calories']:.0f} kcal")
        
        st.divider()
        
        if st.button("💾 Save Custom Goals", use_container_width=True, key="save_custom_btn"):
            custom_goals = {
                'daily_calories': custom_calories,
                'protein_grams': custom_protein,
                'carbs_grams': custom_carbs,
                'fat_grams': custom_fat,
                'calorie_deficit': custom_deficit
            }
            
            if save_custom_recommendations(user_id, custom_goals):
                st.success("✅ Custom goals saved!")
                st.rerun()
            else:
                st.error("❌ Failed to save custom goals")


if __name__ == "__main__":
    settings_recommendations_page()
