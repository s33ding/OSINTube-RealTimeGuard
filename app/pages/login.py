import streamlit as st
import config

# Page config
st.set_page_config(
    page_title="OSINTube - Login",
    page_icon="🔐",
    layout="centered"
)

# Check if already authenticated
from shared_func.cognito_func import is_authenticated, get_current_user
if is_authenticated():
    st.success(f"✅ Already logged in as {get_current_user()}")
    st.info("👈 Use the sidebar to navigate to different pages")
    st.stop()

# Login page
st.title("🔐 OSINTube Login")
st.markdown("---")

# Get Cognito domain
cognito_domain = config.get_parameter('/osintube/cognito_domain')
client_id = config.cognito_client_id

# Import the function to get dynamic redirect URI
from shared_func.cognito_func import get_redirect_uri

# Use dynamic redirect URI based on environment
redirect_uri = get_redirect_uri()

# Cognito Hosted UI URL
login_url = f"https://{cognito_domain}.auth.us-east-1.amazoncognito.com/login?client_id={client_id}&response_type=code&scope=email+openid+profile&redirect_uri={redirect_uri}"

st.markdown("### 🚀 Access OSINTube System")
st.info("🔒 **Restricted Access**: Only authorized IESB personnel can access this system.")

# Login button that redirects to Cognito
st.markdown(f"""
<div style="text-align: center; margin: 2rem 0;">
    <a href="{login_url}" target="_self" style="
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem 2rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.2rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        transition: all 0.3s ease;
    ">
        🔐 Login with AWS Cognito
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("📧 **Authorized Email**: roberto.diniz@iesb.edu.br")
st.warning("⚠️ You will be prompted to change your password on first login.")
