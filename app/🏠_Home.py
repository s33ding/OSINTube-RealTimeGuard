# Set page config first
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from shared_func.cognito_func import is_authenticated

# Check authentication before setting sidebar
if is_authenticated():
    st.set_page_config(
        page_title="OSINTube-RealTimeGuard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
else:
    st.set_page_config(
        page_title="OSINTube - Login",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

# Execute home functionality
exec(open(os.path.join(os.path.dirname(__file__), "home.py")).read())
