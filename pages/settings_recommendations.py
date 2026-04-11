"""
Settings & Recommendations page for HealthTracker.
Allows users to view and customize calorie and macro recommendations.
"""

import streamlit as st
import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from database import get_user, get_settings, update_settings, update_user_profile
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
    tab1, tab2 = st.tabs(["👤 Profile & Goals", "🎯 Recommendations"])
    
    with tab1:
        st.subheader("Your Profile & Goals")
        
        # Initialize edit mode state
        if 'edit_profile_mode' not in st.session_state:
            st.session_state.edit_profile_mode = False
        
        # Edit button
        col_btn1, col_btn2 = st.columns([0.2, 0.8])
        with col_btn1:
            if st.button("✏️ Edit Profile" if not st.session_state.edit_profile_mode else "❌ Cancel", 
                        width='stretch', key="toggle_edit_btn"):
                st.session_state.edit_profile_mode = not st.session_state.edit_profile_mode
                st.rerun()
        
        st.divider()
        
        # Calculate weight to lose (needed for later use in tab2)
        weight_to_lose = user['current_weight'] - user['target_weight']
        
        if not st.session_state.edit_profile_mode:
            # Display Mode - Show metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Current Weight", f"{user['current_weight']} kg")
                st.metric("Target Weight", f"{user['target_weight']} kg")
                st.metric("Weight to Lose", f"{weight_to_lose} kg")
            
            with col2:
                st.metric("Age", f"{user['age']} years")
                st.metric("Height", f"{user['height']} cm")
                st.metric("Gender", user['gender'])
        
        else:
            # Edit Mode - Show input fields
            st.markdown("### 📝 Edit Your Profile")
            
            col1, col2 = st.columns(2)
            
            with col1:
                edit_current_weight = st.number_input(
                    "Current Weight (kg)",
                    min_value=20.0,
                    max_value=500.0,
                    value=float(user['current_weight']),
                    step=0.1,
                    key="edit_current_weight"
                )
                
                edit_target_weight = st.number_input(
                    "Target Weight (kg)",
                    min_value=20.0,
                    max_value=500.0,
                    value=float(user['target_weight']),
                    step=0.1,
                    key="edit_target_weight"
                )
                
                edit_age = st.number_input(
                    "Age (years)",
                    min_value=10,
                    max_value=120,
                    value=int(user['age']),
                    step=1,
                    key="edit_age"
                )
            
            with col2:
                edit_height = st.number_input(
                    "Height (cm)",
                    min_value=100,
                    max_value=250,
                    value=int(user['height']),
                    step=1,
                    key="edit_height"
                )
                
                edit_gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    index=["Male", "Female", "Other"].index(user['gender']),
                    key="edit_gender"
                )
            
            # Show calculated weight to lose
            edit_weight_to_lose = edit_current_weight - edit_target_weight
            st.info(f"📊 **Weight to Lose:** {edit_weight_to_lose:.1f} kg")
            
            # Save button
            if st.button("💾 Save Profile Changes", width='stretch', key="save_profile_btn"):
                profile_updates = {
                    'age': edit_age,
                    'height': edit_height,
                    'current_weight': edit_current_weight,
                    'target_weight': edit_target_weight,
                    'gender': edit_gender
                }
                
                if update_user_profile(user_id, **profile_updates):
                    st.success("✅ Profile updated successfully!")
                    st.session_state.edit_profile_mode = False
                    st.rerun()
                else:
                    st.error("❌ Failed to update profile")
        
        st.divider()
        
        st.subheader("Preferences for Recommendations")
        
        # Add detailed explanation about preferences
        with st.expander("📚 How Preferences Work", expanded=False):
            st.markdown("""
            ### Understanding Your Preferences:
            
            These three settings determine how your personalized calorie and macro targets are calculated:
            
            **1️⃣ Activity Level** - How much you exercise per week
            - **Sedentary:** Little or no exercise, desk job
            - **Light:** Exercise 1-3 days/week
            - **Moderate:** Exercise 3-5 days/week (recommended starting point)
            - **Very Active:** Exercise 6-7 days/week
            - **Extremely Active:** Physical job or training twice per day
            
            *Impact:* Higher activity = higher daily calorie allowance (more calories to burn)
            
            **2️⃣ Diet Preference** - Your preferred macro distribution
            - **Balanced:** 25% Protein, 50% Carbs, 25% Fat (neutral, general fitness)
            - **High Protein:** 35% Protein, 40% Carbs, 25% Fat (muscle building)
            - **Low Carb:** 30% Protein, 25% Carbs, 45% Fat (steady energy, keto-style)
            - **Vegetarian:** 20% Protein, 50% Carbs, 30% Fat (plant-based focus)
            
            *Impact:* Changes your daily protein/carbs/fat targets while keeping calories same. **Fiber target adjusts automatically based on your calorie intake (14g per 1000 calories).**
            
            **3️⃣ Weekly Weight Loss Target** - How fast you want to lose weight
            - **0.25 kg/week:** Very gradual, minimal lifestyle change
            - **0.5 kg/week:** Moderate, sustainable (recommended)
            - **0.75 kg/week:** Aggressive, requires discipline
            - **1.0 kg/week:** Very aggressive, requires significant deficit
            
            *Impact:* Higher target = lower daily calorie allowance = larger deficit
            
            💡 **Tip:** Start with Moderate activity + Balanced diet + 0.5 kg/week loss
            """)
        
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
        
        if st.button("💾 Save Preferences", width='stretch', key="save_prefs_btn"):
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
        
        # Add expandable section explaining BMR and TDEE
        with st.expander("📖 Understanding BMR, TDEE & Calorie Needs", expanded=False):
            # Pre-calculate values for formatting
            bmr = calculated_rec['bmr']
            tdee = calculated_rec['tdee']
            daily_calories = calculated_rec['daily_calories']
            deficit = calculated_rec['calorie_deficit']
            fiber_target = calculated_rec['fiber_grams']
            multiplier = tdee / bmr
            diet_only_calories = daily_calories
            exercise_calories = deficit
            combined_eat = daily_calories - (deficit / 2)
            combined_burn = deficit / 2
            weekly_deficit = deficit * 7
            
            st.markdown(f"""
            ### Key Concepts:
            
            **📌 BMR (Basal Metabolic Rate):** {bmr:.0f} kcal/day
            - The minimum calories your body burns **at rest** just to function
            - Covers: heart beating, breathing, cell production, etc.
            - Doesn't include any exercise or daily activities
            
            **📌 TDEE (Total Daily Energy Expenditure):** {tdee:.0f} kcal/day
            - Total calories your body burns including exercise + daily activities
            - Calculated as: BMR × Activity Level Multiplier
            - For **{current_activity}** activity: BMR × {multiplier:.2f}
            
            ---
            
            ### Your Daily Calorie Plan:
            
            **Daily Calorie Intake (Target):** {daily_calories:.0f} kcal
            - This is what you should **eat** each day
            - Lower than TDEE to create a deficit for weight loss
            
            **Daily Calorie Deficit:** {deficit:.0f} kcal
            - The difference between TDEE and your intake
            - Needed to lose weight (1 kg = 7700 calories)
            - Your {current_target_loss}kg/week goal requires: ~{deficit:.0f}kcal/day deficit
            
            **Daily Fiber Target:** {fiber_target:.0f}g
            - Fiber promotes satiety (feeling full longer)
            - Supports healthy digestion and gut health
            - Based on: 14g per 1000 calories (Institute of Medicine guideline)
            
            **How to Achieve the Deficit:**
            ```
            Option 1: Eat Less
            - Eat {diet_only_calories:.0f} kcal → Creates {exercise_calories:.0f}kcal deficit
            
            Option 2: Exercise More
            - Eat {tdee:.0f} kcal (normal) + Burn {exercise_calories:.0f}kcal through exercise
            
            Option 3: Combine (BEST) 
            - Eat ~{combined_eat:.0f} kcal
            - Burn ~{combined_burn:.0f} kcal through exercise
            - Total deficit: {deficit:.0f} kcal
            ```
            
            ---
            
            ### Weight Loss Math:
            - Daily deficit: {deficit:.0f} kcal
            - Weekly deficit: {weekly_deficit:.0f} kcal
            - kg per week: {current_target_loss:.2f} kg (at current pace)
            - Weeks to goal: {weight_to_lose / current_target_loss:.0f} weeks
            
            💡 **Pro Tip:** Combine diet (eating less) and exercise (burning more) for best results! Prioritize fiber-rich foods for sustainable satiety.
            """)
        
        # Display calculated recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Calculated Recommendations")
            st.metric("Daily Calories (Eat)", f"{calculated_rec['daily_calories']:.0f} kcal")
            st.metric("Exercise Calories (Burn)", f"{calculated_rec['exercise_calories']:.0f} kcal")
            st.metric("Protein", f"{calculated_rec['protein_grams']:.0f}g")
            st.metric("Carbs", f"{calculated_rec['carbs_grams']:.0f}g")
            st.metric("Fat", f"{calculated_rec['fat_grams']:.0f}g")
            st.metric("Fiber", f"{calculated_rec['fiber_grams']:.0f}g")
            st.metric("Daily Deficit Goal", f"{calculated_rec['calorie_deficit']:.0f} kcal")
            
            st.divider()
            st.caption(f"**BMR:** {calculated_rec['bmr']:.0f} kcal/day (at rest)")
            st.caption(f"**TDEE:** {calculated_rec['tdee']:.0f} kcal/day (with {current_activity} activity)")
        
        with col2:
            st.markdown("### 💡 Daily Action Plan")
            st.info(f"**Goal:** Lose {weight_to_lose}kg at {current_target_loss}kg/week")
            st.success(f"**Timeline:** ~{weight_to_lose / current_target_loss:.0f} weeks to reach target")
            
            st.divider()
            st.markdown("**Your Daily Targets:**")
            st.markdown(f"""
            - **Eat:** {calculated_rec['daily_calories']:.0f} kcal
            - **Protein:** {calculated_rec['protein_grams']:.0f}g
            - **Carbs:** {calculated_rec['carbs_grams']:.0f}g
            - **Fat:** {calculated_rec['fat_grams']:.0f}g
            - **Fiber:** {calculated_rec['fiber_grams']:.0f}g
            - **Burn (Exercise):** {calculated_rec['exercise_calories']:.0f} kcal
            - **Net Deficit:** {calculated_rec['calorie_deficit']:.0f} kcal/day
            
            **Result:** ~{current_target_loss}kg weight loss per week
            """)
            
            st.divider()
            st.markdown("**Daily Action Steps:**")
            st.markdown(f"""
            1. **Eat:** {calculated_rec['daily_calories']:.0f} kcal with {calculated_rec['fiber_grams']:.0f}g fiber
            2. **Protein:** Aim for {calculated_rec['protein_grams']:.0f}g for muscle preservation
            3. **Burn:** {calculated_rec['exercise_calories']:.0f} kcal through exercise
            4. **Track:** Log meals + activities + fiber in HealthTracker
            5. **Result:** Lose ~{current_target_loss}kg/week
            """)
            
            st.divider()
            st.markdown("**💬 Recommendations:**")
            for i, tip in enumerate(calculated_rec['tips'], 1):
                st.markdown(f"{i}. {tip}")
        
        st.divider()
        
        # # GPT Recommendations option (DISABLED)
        # st.subheader("🤖 AI-Powered Recommendations (GPT)")
        # st.write("Get personalized recommendations from GPT based on your profile")
        # 
        # if st.button("✨ Generate GPT Recommendations", use_container_width=True, key="gpt_rec_btn"):
        #     with st.spinner("🤖 Getting GPT recommendations..."):
        #         gpt_rec = generate_gpt_recommendations(user_id)
        #     
        #     if gpt_rec:
        #         col1, col2 = st.columns(2)
        #         
        #         with col1:
        #             st.markdown("### 🤖 GPT Recommendations")
        #             st.metric("Daily Calories", f"{gpt_rec['daily_calories']:.0f} kcal")
        #             st.metric("Protein", f"{gpt_rec['protein_grams']:.0f}g")
        #             st.metric("Carbs", f"{gpt_rec['carbs_grams']:.0f}g")
        #             st.metric("Fat", f"{gpt_rec['fat_grams']:.0f}g")
        #             st.metric("Weekly Loss", f"{gpt_rec['weekly_weight_loss']:.2f} kg")
        #         
        #         with col2:
        #             st.markdown("### 📝 AI Reasoning")
        #             st.info(gpt_rec['reasoning'])
        #             st.markdown("**AI Tips:**")
        #             for i, tip in enumerate(gpt_rec['tips'], 1):
        #                 st.markdown(f"{i}. {tip}")
        #         
        #         st.divider()
        #         
        #         if st.button("💾 Use GPT Recommendations", use_container_width=True, key="use_gpt_rec_btn"):
        #             if save_recommendations(user_id, gpt_rec, use_gpt=True):
        #                 st.success("✅ GPT recommendations activated!")
        #                 st.rerun()
        #     else:
        #         st.error("❌ Failed to get GPT recommendations. Check your API key.")
        # 
        # st.divider()
        
        # Automatically use calculated recommendations
        # Note: Recommendations are automatically saved and used for tracking
    
    # # CUSTOM GOALS TAB DISABLED - Using Calculated Recommendations only
    # with tab3:
    #     st.subheader("🎯 Customize Your Goals")
    #     st.write("Override the recommendations with your custom targets")
    #     
    #     # Get current active recommendations as defaults
    #     active_rec = get_active_recommendations(user_id)
    #     
    #     # Use defaults if active_rec values are 0 (not set yet)
    #     default_calories = active_rec['daily_calories'] if active_rec and active_rec['daily_calories'] > 0 else 1800
    #     default_protein = active_rec['protein_grams'] if active_rec and active_rec['protein_grams'] > 0 else 120
    #     default_carbs = active_rec['carbs_grams'] if active_rec and active_rec['carbs_grams'] > 0 else 180
    #     default_fat = active_rec['fat_grams'] if active_rec and active_rec['fat_grams'] > 0 else 60
    #     default_deficit = active_rec['calorie_deficit'] if active_rec and active_rec['calorie_deficit'] > 0 else 500
    #     
    #     col1, col2 = st.columns(2)
    #     
    #     with col1:
    #         custom_calories = st.number_input(
    #             "Daily Calorie Goal (kcal)",
    #             min_value=800.0,
    #             max_value=5000.0,
    #             value=float(default_calories),
    #             step=50.0,
    #             key="custom_cal_input"
    #         )
    #         
    #         custom_protein = st.number_input(
    #             "Daily Protein Goal (g)",
    #             min_value=20.0,
    #             max_value=300.0,
    #             value=float(default_protein),
    #             step=5.0,
    #             key="custom_prot_input"
    #         )
    #     
    #     with col2:
    #         custom_carbs = st.number_input(
    #             "Daily Carbs Goal (g)",
    #             min_value=50.0,
    #             max_value=400.0,
    #             value=float(default_carbs),
    #             step=10.0,
    #             key="custom_carbs_input"
    #         )
    #         
    #         custom_fat = st.number_input(
    #             "Daily Fat Goal (g)",
    #             min_value=20.0,
    #             max_value=150.0,
    #             value=float(default_fat),
    #             step=5.0,
    #             key="custom_fat_input"
    #         )
    #     
    #     custom_deficit = st.number_input(
    #         "Calorie Deficit Constant (kcal/day)",
    #         min_value=100.0,
    #         max_value=1500.0,
    #         value=float(default_deficit),
    #         step=50.0,
    #         help="Daily deficit target for weight loss calculation",
    #         key="custom_deficit_input"
    #     )
    #     
    #     st.divider()
    #     
    #     # Calculate macro breakdown
    #     macros = calculate_macronutrient_percentages(custom_protein, custom_carbs, custom_fat)
    #     
    #     col1, col2, col3 = st.columns(3)
    #     col1.metric("Protein %", f"{macros['protein_percentage']:.1f}%")
    #     col2.metric("Carbs %", f"{macros['carbs_percentage']:.1f}%")
    #     col3.metric("Fat %", f"{macros['fat_percentage']:.1f}%")
    #     
    #     st.info(f"**Total Macros Calories:** {macros['total_calories']:.0f} kcal")
    #     
    #     st.divider()
    #     
    #     if st.button("💾 Save Custom Goals", use_container_width=True, key="save_custom_btn"):
    #         custom_goals = {
    #             'daily_calories': custom_calories,
    #             'protein_grams': custom_protein,
    #             'carbs_grams': custom_carbs,
    #             'fat_grams': custom_fat,
    #             'calorie_deficit': custom_deficit
    #         }
    #         
    #         if save_custom_recommendations(user_id, custom_goals):
    #             st.success("✅ Custom goals saved!")
    #             st.rerun()
    #         else:
    #             st.error("❌ Failed to save custom goals")


if __name__ == "__main__":
    settings_recommendations_page()
