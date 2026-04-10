import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HealthTracker - Calorie & Water Intake Tracker",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title
st.title("🏃 HealthTracker")
st.subheader("Track Your Calories, Water & Weight")

# Placeholder for future content
st.info("🚀 App is under development. Phase 1 setup complete!")

if __name__ == "__main__":
    st.write("Welcome to HealthTracker!")
