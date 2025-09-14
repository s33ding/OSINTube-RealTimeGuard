import streamlit as st
import os
from shared_func.cognito_func import is_authenticated, get_current_user

# Page config
st.set_page_config(
    page_title="OSINTube-RealTimeGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation
if is_authenticated():
    # Authenticated user navigation
    st.sidebar.success(f"✅ Logged in as: {get_current_user()}")
    
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Home", "📊 History", "🚪 Logout"]
    )
    
    if page == "🏠 Home":
        exec(open(os.path.join(os.path.dirname(__file__), "home.py")).read())
    elif page == "📊 History":
        exec(open(os.path.join(os.path.dirname(__file__), "pages/history.py")).read())
    elif page == "🚪 Logout":
        from shared_func.cognito_func import logout_user
        logout_user()
        st.rerun()
else:
    # Not authenticated - show login
    st.sidebar.error("🔒 Not logged in")
    exec(open(os.path.join(os.path.dirname(__file__), "pages/login.py")).read())
