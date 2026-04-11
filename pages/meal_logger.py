"""
Meal Logger page for HealthTracker.
Allows users to log meals, calculate calories using GPT, and view daily meal summaries.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from database import (
    log_meal, get_meals_by_date, delete_meal, save_daily_summary,
    get_daily_summary, get_settings
)
from gpt_utils import calculate_nutrition_for_multiple_meals
from calculations import calculate_macronutrient_percentages


def meal_logger_page():
    """Render the meal logger page."""
    st.title("🍽️ Meal Logger")
    st.markdown("Log your meals and calculate calories using AI")
    
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        st.error("Please login first")
        return
    
    user_id = st.session_state.user_id
    
    # Date selection
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now().date(),
            key="meal_date_picker"
        )
    with col2:
        if st.button("Today", width='stretch'):
            selected_date = datetime.now().date()
    
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    st.divider()
    
    # Get existing meals for the day
    existing_meals = get_meals_by_date(user_id, selected_date_str)
    
    # Tab 1: Add New Meal
    tab1, tab2 = st.tabs(["➕ Add Meal", "📊 Daily Summary"])
    
    with tab1:
        st.subheader("Add a New Meal")
        
        col1, col2 = st.columns(2)
        with col1:
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snack"],
                key="meal_type_select"
            )
        
        with col2:
            meal_time = st.time_input(
                "Time (optional)",
                value=datetime.now().time(),
                key="meal_time_select"
            )
        
        meal_description = st.text_area(
            "Meal Description",
            placeholder="E.g., '2 eggs, 2 slices of toast with butter and jam'\nor 'Grilled chicken 150g with rice and broccoli'\nor '1 banana with 1 tbsp peanut butter'",
            height=80,
            key="meal_description_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            add_meal_button = st.button("➕ Add Meal", width='stretch', key="add_meal_btn")
        with col2:
            clear_button = st.button("Clear", width='stretch', key="clear_meal_btn")
        
        if add_meal_button and meal_description.strip():
            # Log the meal (without GPT analysis yet - will do in batch)
            meal_id = log_meal(
                user_id=user_id,
                date=selected_date_str,
                meal_type=meal_type,
                meal_description=meal_description.strip()
            )
            
            if meal_id:
                st.success(f"✅ Meal added! (ID: {meal_id})")
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to add meal. Please try again.")
        
        elif add_meal_button:
            st.warning("Please enter a meal description")
        
        if clear_button:
            st.rerun()
    
    with tab2:
        st.subheader(f"Daily Summary - {selected_date.strftime('%B %d, %Y')}")
        
        if not existing_meals:
            st.info("📭 No meals logged for this date yet. Add some meals to get started!")
        else:
            # Display logged meals
            st.write(f"**Meals Logged:** {len(existing_meals)}")
            st.divider()
            
            # Create columns for meal display
            for i, meal in enumerate(existing_meals):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{meal['meal_type']}** - {meal['meal_description']}")
                    if meal['calories']:
                        st.caption(f"💡 {meal['calories']} kcal | P:{meal['protein']}g | C:{meal['carbs']}g | F:{meal['fat']}g")
                    else:
                        st.caption("⏳ Waiting for GPT analysis...")
                
                with col2:
                    if st.button("❌", key=f"delete_meal_{meal['id']}", help="Delete meal"):
                        delete_meal(meal['id'])
                        st.success("Meal deleted")
                        st.rerun()
                
                with col3:
                    pass
            
            st.divider()
            
            # Calculate calories button
            if st.button("🤖 Calculate Calories (GPT)", width='stretch', key="calculate_calories_btn"):
                with st.spinner("🔄 Analyzing meals with GPT..."):
                    # Get meals without calories calculated, keeping track of their IDs
                    meals_to_analyze = []
                    meal_ids_to_update = []
                    
                    for meal in existing_meals:
                        if not meal['calories']:
                            meals_to_analyze.append(meal['meal_description'])
                            meal_ids_to_update.append(meal['id'])
                    
                    if meals_to_analyze:
                        result = calculate_nutrition_for_multiple_meals(meals_to_analyze)
                        
                        if result['success_count'] > 0:
                            # Update meals in database with GPT results
                            from database import get_db_connection
                            
                            for i, nutrition in enumerate(result['meal_details']):
                                if i < len(meal_ids_to_update):
                                    meal_id = meal_ids_to_update[i]
                                    
                                    conn = get_db_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        UPDATE nutrition_log
                                        SET calories = ?, protein = ?, carbs = ?, fat = ?, fiber = ?
                                        WHERE id = ?
                                    """, (nutrition['calories'], nutrition['protein'], nutrition['carbs'], 
                                          nutrition['fat'], nutrition['fiber'], meal_id))
                                    conn.commit()
                                    conn.close()
                            
                            st.success(f"✅ Analyzed {result['success_count']} meals!")
                            
                            # Show meal breakdown
                            with st.expander("📊 Meal Breakdown", expanded=False):
                                for nutrition in result['meal_details']:
                                    st.write(f"**{nutrition['meal_description']}**")
                                    col1, col2, col3, col4 = st.columns(4)
                                    col1.metric("Calories", f"{nutrition['calories']} kcal")
                                    col2.metric("Protein", f"{nutrition['protein']}g")
                                    col3.metric("Carbs", f"{nutrition['carbs']}g")
                                    col4.metric("Fat", f"{nutrition['fat']}g")
                                    st.divider()
                            
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to analyze meals. Check your OpenAI API key and try again.")
                    else:
                        st.info("✅ All meals already analyzed!")
            
            # Get updated meals after calculation
            existing_meals = get_meals_by_date(user_id, selected_date_str)
            
            # Display summary stats
            if any(m['calories'] for m in existing_meals):
                st.divider()
                st.subheader("📊 Daily Totals")
                
                total_calories = sum(m['calories'] or 0 for m in existing_meals)
                total_protein = sum(m['protein'] or 0 for m in existing_meals)
                total_carbs = sum(m['carbs'] or 0 for m in existing_meals)
                total_fat = sum(m['fat'] or 0 for m in existing_meals)
                total_fiber = sum(m['fiber'] or 0 for m in existing_meals)
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Calories", f"{total_calories} kcal")
                col2.metric("Protein", f"{total_protein}g")
                col3.metric("Carbs", f"{total_carbs}g")
                col4.metric("Fat", f"{total_fat}g")
                col5.metric("Fiber", f"{total_fiber}g")
                
                # Macronutrient breakdown
                macros = calculate_macronutrient_percentages(total_protein, total_carbs, total_fat)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Macro Breakdown:**")
                    st.markdown(f"- 🥩 Protein: {macros['protein_percentage']}%")
                    st.markdown(f"- 🌾 Carbs: {macros['carbs_percentage']}%")
                    st.markdown(f"- 🧈 Fat: {macros['fat_percentage']}%")
                
                with col2:
                    st.markdown("**Daily Totals:**")
                    st.markdown(f"- Total Calories: {total_calories} kcal")
                    st.markdown(f"- Total Protein: {total_protein}g")
                    st.markdown(f"- Total Carbs: {total_carbs}g")
                    st.markdown(f"- Total Fat: {total_fat}g")
                    st.markdown(f"- Total Fiber: {total_fiber}g")
                
                # Save daily summary button
                if st.button("💾 Save Daily Summary", width='stretch', key="save_summary_btn"):
                    settings = get_settings(user_id)
                    calorie_deficit_constant = settings['calorie_deficit_constant'] if settings else 500
                    
                    save_daily_summary(
                        user_id=user_id,
                        date=selected_date_str,
                        calories_consumed=total_calories,
                        protein=total_protein,
                        carbs=total_carbs,
                        fat=total_fat,
                        fiber=total_fiber
                    )
                    st.success("✅ Daily summary saved!")


if __name__ == "__main__":
    meal_logger_page()
