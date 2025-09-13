import pandas as pd
import streamlit as st
from shared_func.main_func import extract_data
import config
from shared_func.s3_objects import *
from shared_func.dynamodb_func import log_search_to_dynamodb
from shared_func.cognito_func import is_authenticated, get_current_user, logout_user

# Handle OAuth callback once
if 'auth_processed' not in st.session_state:
    query_params = st.query_params
    auth_code = query_params.get('code')
    if auth_code:
        st.session_state.authenticated = True
        st.session_state.user_email = 'roberto.diniz@iesb.edu.br'
        st.session_state.auth_processed = True
        st.rerun()
    st.session_state.auth_processed = True

# Minimal CSS - remove heavy animations
st.markdown("""
<style>
.stApp > header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.main .block-container {padding-top: 0rem;}

.title-text {
    font-family: 'Courier New', monospace;
    font-size: 2rem;
    font-weight: bold;
    text-align: center;
    color: #00ff41;
    margin: 1rem 0;
}

.stats-card {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Check authentication
if not is_authenticated():
    st.markdown('<div class="title-text">🔐 OSINTube Login</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        oauth_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email+openid&redirect_uri=http://localhost:8501"
        st.link_button("🔐 Login with Google", oauth_url, type="primary")
        if st.button("📊 View Public Data", type="secondary"):
            st.switch_page("pages/1_📊_Public_Data.py")
    st.stop()

# User info
col1, col2 = st.columns([3, 1])
with col1:
    st.success(f"✅ Logged in as: {get_current_user()}")
with col2:
    if st.button("🚪 Logout", type="secondary"):
        logout_user()
        st.rerun()

# Simple title
st.markdown('<div class="title-text">OSINTube - Real-Time Guard</div>', unsafe_allow_html=True)

# Simple stats
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="stats-card"><h4>🎯 Threat Level</h4><p>Status: ACTIVE</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stats-card"><h4>📊 Analysis Engine</h4><p>Model: Llama 4 Scout</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stats-card"><h4>🌐 Data Sources</h4><p>YouTube API: Connected</p></div>', unsafe_allow_html=True)

# Configuration
st.markdown("### ⚙️ Configuration")
col1, col2 = st.columns(2)
with col1:
    comments_maxResult = st.number_input("Max Comments", min_value=10, max_value=200, value=10, step=10)
with col2:
    search_limit = st.number_input("Max Videos", min_value=1, max_value=20, value=1, step=1)

config.comments_maxResult = comments_maxResult
config.search_limit = search_limit

# Input section
st.markdown("### 🔍 Threat Analysis")
col1, col2, col3 = st.columns([6, 1.5, 1.5])
with col1:
    input_data = st.text_input("Enter YouTube search query:")
with col2:
    run_button = st.button("▶️ Run", type="primary")
with col3:
    stop_button = st.button("🛑 Stop", type="secondary")

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False

# Handle buttons
if stop_button:
    st.session_state.stop_requested = True
    st.session_state.processing = False
    st.warning("⏹️ Process stopped")

if run_button and input_data and not st.session_state.stop_requested:
    st.session_state.processing = True
    
    with st.spinner('🔍 Analyzing...'):
        try:
            df = extract_data(input_data, search_limit, comments_maxResult)
            st.success(f"✅ Found {len(df)} comments")
            st.dataframe(df, use_container_width=True)
            
            # S3 upload
            key_word = normalize_key_name(input_data)
            s3_key = f"dataset/{key_word}/{config.default_file_name}"
            upload_dataframe_to_s3(df, config.bucket_name, s3_key, config.output_path, config.delete_file)
            st.info("📤 Uploaded to S3")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        finally:
            st.session_state.processing = False

# Credits
st.markdown("---")
st.markdown("**👨💻 Developed by Roberto Moreira Diniz**")
