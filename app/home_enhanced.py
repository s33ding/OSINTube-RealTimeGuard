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

# Enhanced CSS with critical data highlighting
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
}

/* Critical data highlighting */
.critical-row {
    background-color: #ff4444 !important;
    color: white !important;
    font-weight: bold;
}

.high-threat {
    background-color: #ff6b6b !important;
    color: white !important;
}

.medium-threat {
    background-color: #ffa500 !important;
    color: black !important;
}

.low-threat {
    background-color: #90EE90 !important;
    color: black !important;
}

.threat-indicator {
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: bold;
    display: inline-block;
    margin: 2px;
}

.critical-comment {
    border-left: 4px solid #ff4444;
    padding-left: 10px;
    background-color: rgba(255, 68, 68, 0.1);
}
</style>
""", unsafe_allow_html=True)

def highlight_critical_data(df):
    """Add HTML highlighting to critical threat data"""
    if df.empty:
        return df
    
    # Create a copy for styling
    styled_df = df.copy()
    
    # Define threat keywords
    critical_keywords = ['threat', 'kill', 'bomb', 'attack', 'hate', 'violence', 'terrorist']
    high_keywords = ['angry', 'fight', 'destroy', 'revenge', 'war']
    
    def get_threat_level(text):
        if pd.isna(text):
            return 'safe'
        text_lower = str(text).lower()
        if any(word in text_lower for word in critical_keywords):
            return 'critical'
        elif any(word in text_lower for word in high_keywords):
            return 'high'
        return 'safe'
    
    # Add threat level column
    if 'comment' in styled_df.columns:
        styled_df['threat_level'] = styled_df['comment'].apply(get_threat_level)
        
        # Create HTML formatted comments
        def format_comment(row):
            comment = str(row['comment'])
            threat_level = row['threat_level']
            
            if threat_level == 'critical':
                return f'<div class="critical-comment"><span class="threat-indicator critical-row">🚨 CRITICAL</span><br>{comment}</div>'
            elif threat_level == 'high':
                return f'<div><span class="threat-indicator high-threat">⚠️ HIGH</span><br>{comment}</div>'
            else:
                return comment
        
        styled_df['formatted_comment'] = styled_df.apply(format_comment, axis=1)
    
    return styled_df

def display_enhanced_dataframe(df):
    """Display dataframe with enhanced HTML formatting"""
    if df.empty:
        st.warning("⚠️ No data to display")
        return
    
    enhanced_df = highlight_critical_data(df)
    
    # Count threat levels
    if 'threat_level' in enhanced_df.columns:
        critical_count = len(enhanced_df[enhanced_df['threat_level'] == 'critical'])
        high_count = len(enhanced_df[enhanced_df['threat_level'] == 'high'])
        
        # Display threat summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🚨 Critical Threats", critical_count)
        with col2:
            st.metric("⚠️ High Threats", high_count)
        with col3:
            st.metric("📊 Total Comments", len(enhanced_df))
        
        # Filter options
        st.markdown("### 🔍 Filter by Threat Level")
        filter_option = st.selectbox(
            "Show:",
            ["All Comments", "Critical Only", "High & Critical", "Safe Only"]
        )
        
        # Apply filters
        if filter_option == "Critical Only":
            display_df = enhanced_df[enhanced_df['threat_level'] == 'critical']
        elif filter_option == "High & Critical":
            display_df = enhanced_df[enhanced_df['threat_level'].isin(['critical', 'high'])]
        elif filter_option == "Safe Only":
            display_df = enhanced_df[enhanced_df['threat_level'] == 'safe']
        else:
            display_df = enhanced_df
        
        # Display formatted comments if available
        if 'formatted_comment' in display_df.columns and not display_df.empty:
            st.markdown("### 💬 Comments Analysis")
            for idx, row in display_df.iterrows():
                st.markdown(row['formatted_comment'], unsafe_allow_html=True)
                st.markdown("---")
    
    # Display full dataframe
    st.markdown("### 📊 Complete Dataset")
    st.dataframe(enhanced_df, use_container_width=True, height=600)

# Authentication check
if not is_authenticated():
    st.error("🔒 Please authenticate to access this application")
    st.stop()

# Main app content
st.markdown('<div class="title-container"><h1 class="title-text">🥷 OSINTube-RealTimeGuard</h1></div>', unsafe_allow_html=True)

# Configuration
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
            
            # Display enhanced results
            st.success(f"✅ Loaded {len(df)} records")
            display_enhanced_dataframe(df)
                
            st.success("📝 Search logged to history")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        st.session_state.processing = False

# Credits
st.markdown("---")
st.markdown("**👨💻 Developed by Roberto Moreira Diniz**")
