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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Calories",
        "⚖️ Weight",
        "🥗 Macros",
        "💧 Hydration",
        "📊 Summary Stats"
    ])
    
    with tab1:
        st.subheader("Calorie Tracking")
        
        # Get target calories from settings
        target_calories = settings.get('recommended_daily_calories', 2000)
        if target_calories == 0:
            target_calories = 2000  # Default if not set
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calorie consumption vs burned line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['date'].dt.strftime('%Y-%m-%d'),
                y=df['calories_consumed'],
                name='Consumed',
                mode='lines+markers',
                line=dict(color='#FF6B6B', width=2),
                marker=dict(size=6)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['date'].dt.strftime('%Y-%m-%d'),
                y=df['calories_gym'] + df['calories_walk'],
                name='Burned',
                mode='lines+markers',
                line=dict(color='#51CF66', width=2),
                marker=dict(size=6)
            ))
            
            # Add target line
            fig.add_hline(
                y=target_calories,
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Target: {target_calories:.0f}",
                annotation_position="right"
            )
            
            fig.update_layout(
                title="Daily Calories: Consumed vs Burned",
                xaxis_title="Date",
                yaxis_title="Calories (kcal)",
                hovermode='x unified',
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Net calories bar chart
            df['net_calories'] = df['calories_consumed'] - (df['calories_gym'] + df['calories_walk'])
            
            colors = ['#51CF66' if x < 0 else '#FF6B6B' for x in df['net_calories']]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df['date'].dt.strftime('%Y-%m-%d'),
                y=df['net_calories'],
                marker=dict(color=colors),
                name='Net Calories',
                text=[f"{x:.0f}" for x in df['net_calories']],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Daily Net Calories",
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
        avg_net = (df['calories_consumed'] - (df['calories_gym'] + df['calories_walk'])).mean()
        
        with col1:
            st.metric("Avg Consumed", f"{avg_consumed:.0f} kcal", 
                     delta=f"{avg_consumed - target_calories:+.0f} vs target")
        
        with col2:
            st.metric("Avg Burned", f"{avg_burned:.0f} kcal")
        
        with col3:
            st.metric("Avg Net", f"{avg_net:.0f} kcal",
                     delta="Deficit" if avg_net < 0 else "Surplus")
    
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
        
        # Average macros
        df_with_macros = df[df['protein'] > 0].copy()
        
        if len(df_with_macros) == 0:
            st.warning("⚠️ No macro data available yet")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Macro trend
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_with_macros['date'].dt.strftime('%Y-%m-%d'),
                    y=df_with_macros['protein'],
                    name='Protein',
                    mode='lines+markers'
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_with_macros['date'].dt.strftime('%Y-%m-%d'),
                    y=df_with_macros['carbs'],
                    name='Carbs',
                    mode='lines+markers'
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_with_macros['date'].dt.strftime('%Y-%m-%d'),
                    y=df_with_macros['fat'],
                    name='Fat',
                    mode='lines+markers'
                ))
                
                fig.update_layout(
                    title="Macronutrient Trends",
                    xaxis_title="Date",
                    yaxis_title="Grams (g)",
                    hovermode='x unified',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Average macro pie chart
                avg_protein = df_with_macros['protein'].mean()
                avg_carbs = df_with_macros['carbs'].mean()
                avg_fat = df_with_macros['fat'].mean()
                
                fig = go.Figure(data=[go.Pie(
                    labels=['Protein', 'Carbs', 'Fat'],
                    values=[avg_protein, avg_carbs, avg_fat],
                    marker=dict(colors=['#FF6B6B', '#4ECDC4', '#FFE66D'])
                )])
                
                fig.update_layout(
                    title="Average Macro Distribution",
                    height=400
                )
                
                st.plotly_chart(fig, width='stretch')
            
            # Macro stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg Protein", f"{avg_protein:.0f}g")
            
            with col2:
                st.metric("Avg Carbs", f"{avg_carbs:.0f}g")
            
            with col3:
                st.metric("Avg Fat", f"{avg_fat:.0f}g")
    
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


if __name__ == "__main__":
    analytics_page()
