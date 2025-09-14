import pandas as pd
import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from config_loader import get_base_url
import config
from shared_func.s3_objects import *
from shared_func.llama_agent import analyze_dataset_with_llama
from shared_func.dynamodb_func import log_search_to_dynamodb
from shared_func.cognito_func import is_authenticated, get_current_user, logout_user
import pyfiglet

# Check authentication - redirect to login if not authenticated
if not is_authenticated():
    st.switch_page("pages/login.py")

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

.title-container {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3, #54a0ff);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    text-align: center;
    white-space: pre;
    font-size: 14px;
    line-height: 1.1;
    animation: gradientShift 3s ease-in-out infinite;
}

.cyber-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.5rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(45deg, #00ff41, #0080ff, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: pulse 2s infinite;
    margin: 1rem 0;
}

.emoji-title {
    font-size: 2.5rem;
    text-align: center;
    margin: 1rem 0;
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.8);
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes pulse {
    0% { text-shadow: 0 0 30px rgba(0,255,65,0.7); }
    50% { text-shadow: 0 0 50px rgba(0,255,65,1); }
    100% { text-shadow: 0 0 30px rgba(0,255,65,0.7); }
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
    # ASCII title with animation for login
    ascii_title = pyfiglet.figlet_format('OSINTube', font='big')
    st.markdown(f'<div class="title-container">{ascii_title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="emoji-title">🔐 LOGIN REQUIRED 🔐</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Determine redirect URI based on environment
        import os
        redirect_uri = get_base_url()
        
        # Use config values instead of hardcoded
        cognito_domain = config.get_parameter('/osintube/cognito_domain')
        client_id = config.cognito_client_id
        oauth_url = f"https://{cognito_domain}.auth.us-east-1.amazoncognito.com/oauth2/authorize?client_id={client_id}&response_type=code&scope=email+openid&redirect_uri={redirect_uri}"
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

# ASCII title with animation
ascii_title = pyfiglet.figlet_format('OSINTube', font='big')
st.markdown(f'<div class="title-container">{ascii_title}</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-title">🛡️ REAL-TIME GUARD 🛡️</div>', unsafe_allow_html=True)

# Simple stats
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="stats-card"><h4>🎯 Threat Level</h4><p>Status: ACTIVE</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stats-card"><h4>📊 Analysis Engine</h4><p>Model: AWS Comprehend</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stats-card"><h4>🌐 Data Sources</h4><p>YouTube API: Connected</p></div>', unsafe_allow_html=True)

# Configuration
st.markdown("### ⚙️ Configuration")
col1, col2 = st.columns(2)
with col1:
    comments_maxResult = st.number_input("Max Comments", min_value=10, max_value=200, value=30, step=10)
with col2:
    search_limit = st.number_input("Max Videos", min_value=1, max_value=20, value=5, step=1)

config.comments_maxResult = comments_maxResult
config.search_limit = search_limit

# Input section
st.markdown("### 🔍 Analysis")
input_data = st.text_input("Enter YouTube search query:")

col1, col2, col3 = st.columns([6, 1.5, 1.5])
with col1:
    pass
with col2:
    run_button = st.button("▶️ Run", type="primary")
with col3:
    stop_button = st.button("⏹️ Stop", type="secondary")

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

# Reset stop state when run is clicked
if run_button:
    st.session_state.stop_requested = False

if run_button and input_data:
    st.session_state.processing = True
    
    # Progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text('🎥 Searching YouTube videos...')
        progress_bar.progress(20)
        
        df = extract_data(input_data, search_limit, comments_maxResult)
        
        status_text.text('💬 Processing comments...')
        progress_bar.progress(60)
        
        if df.empty:
            st.warning("⚠️ No data found for this search")
        else:
            status_text.text('📤 Uploading to S3...')
            progress_bar.progress(80)
            
            # S3 upload with timestamp suffix
            from datetime import datetime
            timestamp_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            key_word = normalize_key_name(input_data)
            s3_key = f"dataset/{key_word}_{timestamp_suffix}/{config.default_file_name}"
            upload_dataframe_to_s3(df, config.bucket_name, s3_key, config.output_path, config.delete_file)
            
            status_text.text('📝 Logging to database...')
            progress_bar.progress(90)
            
            # Log to DynamoDB
            comments_found = len(df)
            log_search_to_dynamodb(input_data, s3_key, comments_maxResult, search_limit, comments_found)
            
            status_text.text('✅ Complete!')
            progress_bar.progress(100)
            
            # Display results
            st.success(f"✅ Loaded {len(df)} records")
            st.dataframe(df, use_container_width=True, height=800)
                
            st.success("📝 Search logged to history")
            
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        st.session_state.processing = False

# Credits - CI/CD Test
st.markdown("---")
st.markdown("**👨💻 Developed by Roberto Moreira Diniz**")
