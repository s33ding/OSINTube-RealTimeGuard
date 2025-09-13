# Set page config first
import streamlit as st
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
exec(open("home.py").read())
