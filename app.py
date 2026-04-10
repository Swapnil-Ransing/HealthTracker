import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Import database initialization
from db.database import init_db, get_user, get_settings, get_family_members

# Import authentication functions
from utils.auth import register_user, login_user, get_user_info

# Page configuration
st.set_page_config(
    page_title="HealthTracker - Calorie & Water Intake Tracker",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
    }
    .welcome-header {
        text-align: center;
        padding: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database on first run
if not os.path.exists("db/data.db"):
    init_db()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'page' not in st.session_state:
    st.session_state.page = "login"  # login, signup, dashboard


def show_login_page():
    """Display login page."""
    st.markdown('<div class="welcome-header"><h1>🏃 HealthTracker</h1><p>Track Your Health Journey</p></div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("👤 **Existing User?** Login below")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if username and password:
                    success, message, user_id = login_user(username, password)
                    
                    if success:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        user_info = get_user_info(user_id)
                        st.session_state.user_name = user_info['user']['name']
                        st.session_state.page = "dashboard"
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both username and password")
    
    with col2:
        st.info("✨ **New User?** Create account below")
        if st.button("Sign Up Now →", use_container_width=True, key="signup_btn"):
            st.session_state.page = "signup"
            st.rerun()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    HealthTracker v1.0 | Track your calories, water, and weight effortlessly
    </div>
    """, unsafe_allow_html=True)


def show_signup_page():
    """Display signup page with profile creation."""
    st.markdown('<div class="welcome-header"><h1>🎉 Create Your Account</h1><p>Start Your Health Journey Today</p></div>', 
                unsafe_allow_html=True)
    
    with st.form("signup_form"):
        # Account Information
        st.subheader("📝 Account Information")
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", placeholder="Choose a username (3-20 characters)")
        with col2:
            password = st.text_input("Password", type="password", placeholder="Create a strong password (6+ characters)")
        
        # Personal Information
        st.subheader("👤 Personal Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Full Name", placeholder="Your full name")
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with col3:
            age = st.number_input("Age", min_value=10, max_value=120, value=25)
        
        # Health Measurements
        st.subheader("📊 Health Measurements")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        with col2:
            current_weight = st.number_input("Current Weight (kg)", min_value=20.0, max_value=500.0, value=70.0, step=0.1)
        with col3:
            target_weight = st.number_input("Target Weight (kg)", min_value=20.0, max_value=500.0, value=65.0, step=0.1)
        
        # Family Setup
        st.subheader("👨‍👩‍👧‍👦 Family Setup")
        family_option = st.radio(
            "Do you want to:",
            ["Create a new family", "Join an existing family"],
            horizontal=True
        )
        
        family_name = None
        family_code = None
        
        if family_option == "Create a new family":
            family_name = st.text_input("Family Name", placeholder="e.g., Smith Family, Team Fitness")
        else:
            family_code = st.text_input("Family Code", placeholder="Enter the 6-character family code", max_chars=6)
        
        # Submit button
        signup_button = st.form_submit_button("Create Account", use_container_width=True)
        
        if signup_button:
            if username and password and name:
                family_opt = "create_new" if family_option == "Create a new family" else "join_existing"
                
                success, message, user_id = register_user(
                    username=username,
                    password=password,
                    name=name,
                    gender=gender,
                    age=age,
                    height=height,
                    current_weight=current_weight,
                    target_weight=target_weight,
                    family_option=family_opt,
                    family_name=family_name,
                    family_code=family_code.upper() if family_code else None
                )
                
                if success:
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.session_state.user_name = name
                    st.session_state.page = "dashboard"
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all required fields")
    
    # Back button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


def show_dashboard():
    """Display main dashboard (placeholder for now)."""
    user_info = get_user_info(st.session_state.user_id)
    user = user_info['user']
    family_members = user_info['family_members']
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.divider()
        
        # User info
        if user:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Age", f"{user['age']} yrs")
            with col2:
                st.metric("Height", f"{user['height']} cm")
            
            st.metric("Current Weight", f"{user['current_weight']} kg")
            st.metric("Target Weight", f"{user['target_weight']} kg")
        
        st.divider()
        
        # Family members
        if family_members:
            st.subheader("👨‍👩‍👧‍👦 Family Members")
            for member in family_members:
                st.write(f"• {member['name']} (@{member['username']})")
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.user_name = None
            st.session_state.page = "login"
            st.rerun()
    
    # Main content
    st.title(f"🏃 Welcome back, {st.session_state.user_name}!")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Meal Logger", "Water Tracker", "Analytics", "Settings"])
    
    with tab1:
        st.info("📊 Dashboard - Coming in next phases")
    
    with tab2:
        # Import and display meal logger
        from pages.meal_logger import meal_logger_page
        meal_logger_page()
    
    with tab3:
        # Import and display water tracker
        from pages.water_tracker import water_tracker_page
        water_tracker_page()
    
    with tab4:
        st.info("📈 Analytics - Coming in Phase 7")
    
    with tab5:
        st.info("⚙️ Settings - Coming in Phase 8")


def main():
    """Main app logic."""
    if st.session_state.user_id:
        # User is logged in
        show_dashboard()
    else:
        # User is not logged in
        if st.session_state.page == "signup":
            show_signup_page()
        else:
            show_login_page()


if __name__ == "__main__":
    main()
