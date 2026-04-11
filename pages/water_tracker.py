"""
Water Tracker page for HealthTracker.
Allows users to log water intake, track hydration status, and view daily water goals.
"""

import streamlit as st
from datetime import datetime
import sys
sys.path.insert(0, 'db')
sys.path.insert(0, 'utils')

from database import (
    log_water, get_water_log_by_date, get_total_water_by_date,
    get_settings, update_settings, save_daily_summary, get_daily_summary
)
from calculations import get_hydration_status


def water_tracker_page():
    """Render the water tracker page."""
    st.title("💧 Water Tracker")
    st.markdown("Track your daily water intake and stay hydrated")
    
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
            key="water_date_picker"
        )
    with col2:
        if st.button("Today", width='stretch', key="water_today_btn"):
            selected_date = datetime.now().date()
    
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    st.divider()
    
    # Get user settings
    settings = get_settings(user_id)
    daily_water_goal = settings['daily_water_goal_liters'] if settings else 3.0
    
    # Get today's water intake
    total_water = get_total_water_by_date(user_id, selected_date_str)
    water_entries = get_water_log_by_date(user_id, selected_date_str)
    
    # Display current progress
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Daily Goal",
            f"{daily_water_goal}L",
            help="Target water intake for the day"
        )
    
    with col2:
        st.metric(
            "Current Intake",
            f"{total_water}L",
            f"{total_water} / {daily_water_goal}L"
        )
    
    # Progress bar
    progress_percentage = min((total_water / daily_water_goal) * 100, 100)
    st.progress(progress_percentage / 100, text=f"{progress_percentage:.1f}% of daily goal")
    
    # Hydration status
    hydration = get_hydration_status(total_water, daily_water_goal)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", hydration['status'])
    with col2:
        st.metric("Percentage", f"{hydration['percentage']}%")
    with col3:
        st.metric("Remaining", f"{hydration['remaining']}L")
    
    st.divider()
    
    # Tab 1: Quick Add
    tab1, tab2, tab3 = st.tabs(["➕ Quick Add", "📝 Manual Entry", "📊 Water Log"])
    
    with tab1:
        st.subheader("Quick Add Water")
        st.markdown("Click buttons to quickly log common water amounts")
        
        # Quick add buttons
        col1, col2, col3, col4 = st.columns(4)
        
        amounts = [
            (col1, "250ml", 0.25),
            (col2, "500ml", 0.5),
            (col3, "750ml", 0.75),
            (col4, "1L", 1.0)
        ]
        
        for col, label, amount in amounts:
            with col:
                if st.button(label, width='stretch', key=f"water_quick_{label}"):
                    water_id = log_water(
                        user_id=user_id,
                        date=selected_date_str,
                        water_liters=amount,
                        time=datetime.now().strftime('%H:%M')
                    )
                    
                    if water_id:
                        st.success(f"✅ Added {label}!")
                        st.balloons()
                        st.rerun()
        
        st.divider()
        
        # Custom quick button
        st.markdown("**Custom Amount**")
        custom_amount = st.number_input(
            "Amount (liters)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1,
            key="water_custom_amount"
        )
        
        if st.button("➕ Add Custom Amount", width='stretch', key="water_custom_btn"):
            water_id = log_water(
                user_id=user_id,
                date=selected_date_str,
                water_liters=custom_amount,
                time=datetime.now().strftime('%H:%M')
            )
            
            if water_id:
                st.success(f"✅ Added {custom_amount}L!")
                st.rerun()
    
    with tab2:
        st.subheader("Manual Water Entry")
        
        col1, col2 = st.columns(2)
        
        with col1:
            manual_amount = st.number_input(
                "Water Amount (liters)",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
                key="water_manual_input"
            )
        
        with col2:
            manual_time = st.time_input(
                "Time",
                value=datetime.now().time(),
                key="water_manual_time"
            )
        
        if st.button("📝 Log Water Entry", width='stretch', key="water_manual_log_btn"):
            water_id = log_water(
                user_id=user_id,
                date=selected_date_str,
                water_liters=manual_amount,
                time=manual_time.strftime('%H:%M')
            )
            
            if water_id:
                st.success(f"✅ Logged {manual_amount}L at {manual_time.strftime('%H:%M')}")
                st.rerun()
    
    with tab3:
        st.subheader("Water Log Details")
        
        if not water_entries:
            st.info("📭 No water logged for this date yet.")
        else:
            st.write(f"**Total Entries:** {len(water_entries)}")
            st.divider()
            
            # Display water entries in a table-like format
            for entry in water_entries:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    entry_time = entry['time'] if entry['time'] else "No time"
                    st.markdown(f"⏰ **{entry_time}**")
                
                with col2:
                    st.markdown(f"💧 **{entry['water_intake_liters']}L**")
                
                with col3:
                    if st.button("🗑️", key=f"delete_water_{entry['id']}", help="Delete entry"):
                        from database import get_db_connection
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM water_log WHERE id = ?", (entry['id'],))
                        conn.commit()
                        conn.close()
                        st.success("Entry deleted")
                        st.rerun()
            
            st.divider()
            st.markdown(f"**Daily Total: {total_water}L**")
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Water Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_daily_goal = st.number_input(
            "Daily Water Goal (liters)",
            min_value=1.0,
            max_value=5.0,
            value=daily_water_goal,
            step=0.1,
            key="water_goal_input"
        )
    
    with col2:
        if st.button("💾 Update Goal", width='stretch', key="water_goal_btn"):
            if update_settings(user_id, water_goal=new_daily_goal):
                st.success(f"✅ Daily water goal updated to {new_daily_goal}L")
                st.rerun()


if __name__ == "__main__":
    water_tracker_page()
