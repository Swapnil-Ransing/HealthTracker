"""
Analytics & Graphs page for HealthTracker.
Provides comprehensive visualizations of health data including calories, weight, macros, and hydration.
"""

import streamlit as st
import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from database import (
    get_user, get_daily_summaries_range, get_settings
)
from recommendations import generate_calculated_recommendations
from gpt_utils import generate_performance_insights
import pandas as pd


def analytics_page():
    """Render the analytics and graphs page."""
    st.title("📊 Analytics & Insights")
    st.markdown("Track your progress with comprehensive visualizations")
    
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        st.error("Please login first")
        return
    
    user_id = st.session_state.user_id
    user = get_user(user_id)
    settings = get_settings(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    # Get calculated recommendations for reference lines
    calculated_rec = generate_calculated_recommendations(user_id)
    daily_calories_target = calculated_rec.get('daily_calories', 2000) if calculated_rec else 2000
    exercise_calories_target = calculated_rec.get('exercise_calories', 500) if calculated_rec else 500
    bmr = calculated_rec.get('bmr', 1500) if calculated_rec else 1500
    protein_target = calculated_rec.get('protein_grams', 150) if calculated_rec else 150
    carbs_target = calculated_rec.get('carbs_grams', 200) if calculated_rec else 200
    fat_target = calculated_rec.get('fat_grams', 65) if calculated_rec else 65
    fiber_target = calculated_rec.get('fiber_grams', 30) if calculated_rec else 30
    
    # Calculate net surplus target: daily_calories - exercise_calories - bmr
    net_surplus_target = daily_calories_target - exercise_calories_target - bmr
    
    # Sidebar filters
    with st.sidebar:
        st.subheader("📅 Analytics Filters")
        
        time_range = st.selectbox(
            "Time Range",
            ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 90 Days", "Custom"],
            key="analytics_time_range"
        )
        
        # Calculate date range
        if time_range == "Last 7 Days":
            days = 7
        elif time_range == "Last 14 Days":
            days = 14
        elif time_range == "Last 30 Days":
            days = 30
        elif time_range == "Last 90 Days":
            days = 90
        else:  # Custom
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now().date())
            start_date_str = str(start_date)
            end_date_str = str(end_date)
            data = get_daily_summaries_range(user_id, start_date_str, end_date_str)
        
        if time_range != "Custom":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            start_date_str = str(start_date)
            end_date_str = str(end_date)
            data = get_daily_summaries_range(user_id, start_date_str, end_date_str)
    
    if not data:
        st.warning("❌ No data available for the selected date range")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([dict(row) for row in data])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    st.divider()
    
    # Tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Calories",
        "⚖️ Weight",
        "🥗 Macros",
        "💧 Hydration",
        "📊 Summary Stats",
        "🧠 Insights"
    ])
    
    with tab1:
        st.subheader("Calorie Tracking")
        
        # Use calculated daily calories target
        target_calories = daily_calories_target
        
        colA, colB = st.columns(2)
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

        # ---- Calories Consumed ----
        with colA:
            fig_consumed = go.Figure()

            fig_consumed.add_trace(go.Scatter(
                x=df['date_str'],
                y=df['calories_consumed'],
                name='Consumed',
                mode='lines+markers',
                line=dict(color='#FF6B6B', width=2),
                marker=dict(size=6)
            ))

            fig_consumed.add_hline(
                y=target_calories,
                line_dash="dash",
                line_color="#FF6B6B",
                line_width=1.5,
                annotation_text=f"Target: {target_calories:.0f}",
                annotation_position="right",
                annotation=dict(
                    font=dict(size=12, color="#FF6B6B"),
                    bgcolor="rgba(255,255,255,0.7)"
                )
            )

            fig_consumed.update_layout(
                title="Daily Calories Consumed",
                xaxis_title="Date",
                yaxis_title="Calories (kcal)",
                hovermode='x unified',
                height=300,
                template='plotly_white'
            )

            st.plotly_chart(fig_consumed, width='stretch')
            
        with colB:
            # ---- Calories Burned ----
            df['calories_burned'] = df['calories_gym'] + df['calories_walk']

            fig_burned = go.Figure()

            fig_burned.add_trace(go.Scatter(
                x=df['date_str'],
                y=df['calories_burned'],
                name='Burned',
                mode='lines+markers',
                line=dict(color='#51CF66', width=2),
                marker=dict(size=6)
            ))

            fig_burned.add_hline(
                y=exercise_calories_target,
                line_dash="dash",
                line_color="#51CF66",
                line_width=1.5,
                annotation_text=f"Target: {exercise_calories_target:.0f}",
                annotation_position="right",
                annotation=dict(
                    font=dict(size=12, color="#51CF66"),
                    bgcolor="rgba(255,255,255,0.7)"
                )
            )

            fig_burned.update_layout(
                title="Daily Calories Burned",
                xaxis_title="Date",
                yaxis_title="Calories (kcal)",
                hovermode='x unified',
                height=300,
                template='plotly_white'
            )

            st.plotly_chart(fig_burned, width='stretch')
        
        # Net calories bar chart with net surplus target reference
        df['net_calories'] = df['calories_consumed'] - (df['calories_gym'] + df['calories_walk']) - bmr
        
        colors = ['#51CF66' if x < net_surplus_target else '#FF6B6B' for x in df['net_calories']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['date'].dt.strftime('%Y-%m-%d'),
            y=df['net_calories'],
            marker=dict(color=colors),
            name='Net Calories',
            text=[f"{x:.0f}" for x in df['net_calories']],
            textposition='auto'
        ))
        
        # Add reference line for net surplus target
        fig.add_hline(
            y=net_surplus_target,
            line_dash="dash",
            line_color="#51CF66",
            line_width=1.5,
            annotation_text=f"Target: {net_surplus_target:.0f}",
            annotation_position="right",
            annotation=dict(
                font=dict(size=12, color="#51CF66"),
                bgcolor="rgba(255,255,255,0.7)"
            )
        )
        
        fig.update_layout(
            title="Daily Net Calories (after BMR)",
            xaxis_title="Date",
            yaxis_title="Net Calories (kcal)",
            hovermode='x',
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Calories breakdown
        col1, col2, col3 = st.columns(3)
        
        avg_consumed = df['calories_consumed'].mean()
        avg_burned = (df['calories_gym'] + df['calories_walk']).mean()
        avg_net = (df['calories_consumed'] - (df['calories_gym'] + df['calories_walk']) - bmr).mean()
        
        with col1:
            st.metric("Avg Consumed", f"{avg_consumed:.0f} kcal", 
                     delta=f"{avg_consumed - daily_calories_target:+.0f} vs {daily_calories_target:.0f}")
        
        with col2:
            st.metric("Avg Burned", f"{avg_burned:.0f} kcal",
                     delta=f"{avg_burned - exercise_calories_target:+.0f} vs {exercise_calories_target:.0f}")
        
        with col3:
            st.metric("Avg Net", f"{avg_net:.0f} kcal",
                     delta=f"{avg_net - net_surplus_target:+.0f} vs {net_surplus_target:.0f}")
    
    with tab2:
        st.subheader("Weight Progress")
        
        # Filter out rows without weight
        df_weight = df[df['weight'] > 0].copy()
        
        if len(df_weight) < 2:
            st.warning("⚠️ Need at least 2 weight records to show trend")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Weight trend line chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_weight['date'].dt.strftime('%Y-%m-%d'),
                    y=df_weight['weight'],
                    name='Weight',
                    mode='lines+markers',
                    line=dict(color='#4ECDC4', width=2),
                    marker=dict(size=8, symbol='circle')
                ))
                
                # Add target line
                fig.add_hline(
                    y=user['target_weight'],
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"Goal: {user['target_weight']}kg",
                    annotation_position="right"
                )
                
                fig.update_layout(
                    title="Weight Trend",
                    xaxis_title="Date",
                    yaxis_title="Weight (kg)",
                    hovermode='x unified',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Weight distribution histogram
                fig = go.Figure()
                
                fig.add_trace(go.Histogram(
                    x=df_weight['weight'],
                    nbinsx=10,
                    marker=dict(color='#95E1D3'),
                    name='Distribution'
                ))
                
                fig.add_vline(
                    x=user['target_weight'],
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Target"
                )
                
                fig.update_layout(
                    title="Weight Distribution",
                    xaxis_title="Weight (kg)",
                    yaxis_title="Frequency",
                    height=400,
                    template='plotly_white',
                    showlegend=False
                )
                
                st.plotly_chart(fig, width='stretch')
            
            # Weight stats
            col1, col2, col3, col4 = st.columns(4)
            
            current_weight = df_weight['weight'].iloc[-1]
            start_weight = df_weight['weight'].iloc[0]
            weight_change = current_weight - start_weight
            target_remaining = current_weight - user['target_weight']
            
            with col1:
                st.metric("Current Weight", f"{current_weight:.1f} kg")
            
            with col2:
                st.metric("Weight Change", f"{weight_change:+.1f} kg", 
                         delta=f"from {start_weight:.1f} kg")
            
            with col3:
                st.metric("To Target", f"{target_remaining:.1f} kg")
            
            with col4:
                if target_remaining > 0:
                    progress = ((start_weight - current_weight) / (start_weight - user['target_weight'])) * 100
                    st.metric("Progress", f"{progress:.1f}%")
                else:
                    st.metric("Status", "🎉 Goal Met!", delta_color="off")
    
    with tab3:
        st.subheader("Macronutrient Breakdown")

        df_with_macros = df[df['protein'] > 0].copy()

        if len(df_with_macros) == 0:
            st.warning("⚠️ No macro data available yet")
        else:
            # Create formatted date once
            df_with_macros['date_str'] = df_with_macros['date'].dt.strftime('%Y-%m-%d')

            # ---- ROW 1 ----
            col1, col2 = st.columns(2)

            with col1:
                # Protein
                fig_protein = go.Figure()
                fig_protein.add_trace(go.Scatter(
                    x=df_with_macros['date_str'],
                    y=df_with_macros['protein'],
                    mode='lines+markers',
                    line=dict(color="#F01C1C", width=2)
                ))
                fig_protein.add_hline(y=protein_target, line_dash="dash", line_color="#F01C1C",
                                      annotation_text=f"{protein_target:.0f}g target",
                                      annotation_position="right")
                fig_protein.update_layout(title="Protein", height=300, template='plotly_white')

                st.plotly_chart(fig_protein, width='stretch')

            with col2:
                # Carbs
                fig_carbs = go.Figure()
                fig_carbs.add_trace(go.Scatter(
                    x=df_with_macros['date_str'],
                    y=df_with_macros['carbs'],
                    mode='lines+markers',
                    line=dict(color="#14F0E1", width=2)
                ))
                fig_carbs.add_hline(y=carbs_target, line_dash="dash", line_color="#14F0E1",
                                    annotation_text=f"{carbs_target:.0f}g target",
                                    annotation_position="right")
                fig_carbs.update_layout(title="Carbs", height=300, template='plotly_white')

                st.plotly_chart(fig_carbs, width='stretch')


            # ---- ROW 2 ----
            col3, col4 = st.columns(2)

            with col3:
                # Fat
                fig_fat = go.Figure()
                fig_fat.add_trace(go.Scatter(
                    x=df_with_macros['date_str'],
                    y=df_with_macros['fat'],
                    mode='lines+markers',
                    line=dict(color="#EBC60F", width=2)
                ))
                fig_fat.add_hline(y=fat_target, line_dash="dash", line_color="#EBC60F",
                                  annotation_text=f"{fat_target:.0f}g target",
                                  annotation_position="right")
                fig_fat.update_layout(title="Fat", height=300, template='plotly_white')

                st.plotly_chart(fig_fat, width='stretch')

            with col4:
                # Fiber
                fig_fiber = go.Figure()
                fig_fiber.add_trace(go.Scatter(
                    x=df_with_macros['date_str'],
                    y=df_with_macros['fiber'],
                    mode='lines+markers',
                    line=dict(color="#59F511", width=2)
                ))
                fig_fiber.add_hline(y=fiber_target, line_dash="dash", line_color="#59F511",
                                    annotation_text=f"{fiber_target:.0f}g target",
                                  annotation_position="right")
                fig_fiber.update_layout(title="Fiber", height=300, template='plotly_white')

                st.plotly_chart(fig_fiber, width='stretch')

            # ---- Stats ----
            avg_protein = df_with_macros['protein'].mean()
            avg_carbs = df_with_macros['carbs'].mean()
            avg_fat = df_with_macros['fat'].mean()
            avg_fiber = df_with_macros['fiber'].mean()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Avg Protein", f"{avg_protein:.0f}g",
                        delta=f"{avg_protein - protein_target:+.0f}g vs target")

            with col2:
                st.metric("Avg Carbs", f"{avg_carbs:.0f}g",
                        delta=f"{avg_carbs - carbs_target:+.0f}g vs target")

            with col3:
                st.metric("Avg Fat", f"{avg_fat:.0f}g",
                        delta=f"{avg_fat - fat_target:+.0f}g vs target")

            with col4:
                st.metric("Avg Fiber", f"{avg_fiber:.0f}g",
                        delta=f"{avg_fiber - fiber_target:+.0f}g vs target")
            
    with tab4:
        st.subheader("Hydration Tracking")
        
        # Water intake
        df_water = df[df['water_intake_liters'] > 0].copy()
        
        if len(df_water) == 0:
            st.warning("⚠️ No water tracking data available yet")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily water intake bar chart
                goal_water = settings.get('daily_water_goal_liters', 3.0)
                
                colors = ['#4ECDC4' if x >= goal_water else '#FFE66D' for x in df_water['water_intake_liters']]
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=df_water['date'].dt.strftime('%Y-%m-%d'),
                    y=df_water['water_intake_liters'],
                    marker=dict(color=colors),
                    name='Water Intake',
                    text=[f"{x:.1f}L" for x in df_water['water_intake_liters']],
                    textposition='auto'
                ))
                
                fig.add_hline(
                    y=goal_water,
                    line_dash="dash",
                    line_color="blue",
                    annotation_text=f"Goal: {goal_water}L",
                    annotation_position="right"
                )
                
                fig.update_layout(
                    title="Daily Water Intake",
                    xaxis_title="Date",
                    yaxis_title="Water (Liters)",
                    height=400,
                    template='plotly_white',
                    showlegend=False
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Water goal achievement
                achievement_rate = (df_water['water_intake_liters'] >= goal_water).sum() / len(df_water) * 100
                
                fig = go.Figure(data=[go.Indicator(
                    mode="gauge+number+delta",
                    value=achievement_rate,
                    title={'text': "Goal Achievement %"},
                    delta={'reference': 80},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#4ECDC4"},
                        'steps': [
                            {'range': [0, 50], 'color': "#FFE66D"},
                            {'range': [50, 80], 'color': "#95E1D3"},
                            {'range': [80, 100], 'color': "#51CF66"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                )])
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
            
            # Water stats
            col1, col2, col3 = st.columns(3)
            
            avg_water = df_water['water_intake_liters'].mean()
            
            with col1:
                st.metric("Avg Daily Water", f"{avg_water:.1f} L")
            
            with col2:
                st.metric("Goal", f"{goal_water} L")
            
            with col3:
                st.metric("Achievement", f"{achievement_rate:.0f}%")
    
    with tab5:
        st.subheader("Summary Statistics")
        
        # Overall stats
        st.write("### 📋 Overall Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Days Tracked", len(df))
        
        with col2:
            st.metric("Avg Daily Calories", f"{df['calories_consumed'].mean():.0f} kcal")
        
        with col3:
            total_burned = (df['calories_gym'] + df['calories_walk']).sum()
            st.metric("Total Calories Burned", f"{total_burned:.0f} kcal")
        
        with col4:
            cheat_days = df[df['is_cheat_day'] == 1].shape[0]
            st.metric("Cheat Days", cheat_days)
        
        # Activity stats
        st.write("### 🏋️ Activity Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_gym = df['calories_gym'].mean()
            st.metric("Avg Gym Calories", f"{avg_gym:.0f} kcal")
        
        with col2:
            avg_walk = df['calories_walk'].mean()
            st.metric("Avg Walking Calories", f"{avg_walk:.0f} kcal")
        
        with col3:
            total_exercise = (df['calories_gym'] > 0).sum() + (df['calories_walk'] > 0).sum()
            st.metric("Total Exercise Days", total_exercise)
    
    with tab6:
        st.subheader("🧠 AI-Powered Insights")
        st.markdown("Get personalized insights about your progress and actionable recommendations")

        st.divider()

        # Generate insights button
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("📊 Generate Insights", width='stretch', key="generate_insights_btn"):
                with st.spinner("🤔 Analyzing your performance..."):

                    # Get all data
                    all_data = get_daily_summaries_range(
                        user_id,
                        "2020-01-01",
                        str(datetime.now().date())
                    )

                    if all_data:

                        # ✅ Clean None values
                        cleaned_data = []
                        for row in all_data:
                            cleaned_row = {}
                            for k, v in row.items():
                                if isinstance(v, (int, float)):
                                    cleaned_row[k] = v
                                else:
                                    cleaned_row[k] = 0  # Replace None/invalid with 0
                            cleaned_data.append(cleaned_row)

                        # ✅ Safe time range
                        time_range_days = len(df) if df is not None else 0

                        try:
                            success, insights = generate_performance_insights(
                                user_name=user['name'],
                                recommendations=calculated_rec if calculated_rec else {},
                                daily_summaries=cleaned_data,
                                time_range_days=time_range_days
                            )

                            if success and insights:
                                st.session_state.current_insights = insights
                                st.success("✅ Insights generated!")
                            else:
                                st.error(f"❌ Unable to generate insights: {insights}")

                        except Exception as e:
                            st.error(f"❌ Error generating insights: {str(e)}")

                    else:
                        st.warning("❌ Need at least some data to generate insights")

        st.divider()

        # Display insights
        if 'current_insights' in st.session_state and st.session_state.current_insights:

            st.markdown("""
            <div style="background-color: #f0f8ff; border-left: 4px solid #4ecdc4; 
                        padding: 20px; border-radius: 5px;">
            """, unsafe_allow_html=True)

            st.markdown(st.session_state.current_insights)

            st.markdown("</div>", unsafe_allow_html=True)

            # Export/info section
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.info("💡 Save these insights or share with your fitness coach for personalized guidance!")

        else:
            st.info("👈 Click 'Generate Insights' to get AI-powered analysis of your progress")


if __name__ == "__main__":
    analytics_page()
