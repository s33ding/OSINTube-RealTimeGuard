import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import sys
import os
import boto3
import pickle
from datetime import datetime
import pyfiglet
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared_func.readonly_client import get_readonly_clients
import config

# Page config
st.set_page_config(
    page_title="OSINTube-RealTimeGuard",
    page_icon="🛡️",
    layout="wide"
)

# Same CSS as home page
st.markdown("""
<style>
.stApp > header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.main .block-container {padding-top: 0rem;}

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
    color: #00ff41;
    text-shadow: 0 0 30px rgba(0,255,65,0.7);
    animation: pulse 2s infinite;
    margin: 1rem 0;
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
</style>
""", unsafe_allow_html=True)

# Same animated title as home page
ascii_title = pyfiglet.figlet_format('OSINTube', font='big')
st.markdown(f'<div class="title-container">{ascii_title}</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-title">📊 PUBLIC DATA EXPLORER 📊</div>', unsafe_allow_html=True)

# Available Datasets
st.markdown("### 📋 Available Datasets")

try:
    # Get DynamoDB data
    s3_client, dynamodb_client = get_readonly_clients()
    
    # Scan DynamoDB table
    response = dynamodb_client.scan(TableName='osintube')
    items = response.get('Items', [])
    
    if items:
        # Convert DynamoDB items to DataFrame
        history_data = []
        for item in items:
            history_data.append({
                'Query': item.get('video_query', {}).get('S', ''),
                'Video Title': item.get('video_title', {}).get('S', ''),
                'Comments Found': item.get('comments_found', {}).get('N', '0'),
                'Max Comments': item.get('max_comments', {}).get('N', '0'),
                'Max Videos': item.get('max_videos', {}).get('N', '0'),
                'Search Date': item.get('search_date', {}).get('S', ''),
                'Search Time': item.get('search_time', {}).get('S', ''),
                'Status': item.get('status', {}).get('S', 'unknown'),
                'Timestamp': item.get('timestamp', {}).get('S', ''),
                'S3 Key': item.get('s3', {}).get('S', ''),
                'S3 Full Path': item.get('s3_full_path', {}).get('S', ''),
                'Bucket': item.get('bucket_name', {}).get('S', config.bucket_name)
            })
        
        history_df = pd.DataFrame(history_data)
        history_df = history_df.sort_values('Timestamp', ascending=False)
        
        # Filter and selection
        col1, col2 = st.columns(2)
        with col1:
            search_filter = st.text_input("🔍 Filter datasets:", placeholder="Type to filter...")
        with col2:
            # Create display names with timestamps
            dataset_options = ['']
            for _, row in history_df.iterrows():
                display_name = f"{row['Query']} ({row['Search Date']} {row['Search Time']})"
                dataset_options.append(display_name)
            
            selected_display = st.selectbox(
                "📊 Select Dataset:", 
                options=dataset_options,
                format_func=lambda x: f"{x[:70]}..." if len(x) > 70 else x if x else "Choose a dataset..."
            )
        
        # Apply filter to display
        if search_filter:
            filtered_df = history_df[history_df['Query'].str.contains(search_filter, case=False, na=False)]
        else:
            filtered_df = history_df
        
        # Display available datasets table with all metadata
        st.dataframe(
            filtered_df[['Query', 'Video Title', 'Comments Found', 'Max Comments', 'Max Videos', 'Search Date', 'Search Time', 'Status']], 
            use_container_width=True,
            height=200
        )
        
        # Load S3 data if selected
        if selected_display:
            # Extract original query from display name
            original_query = selected_display.split(' (')[0]
            timestamp_part = selected_display.split(' (')[1].replace(')', '')
            
            # Find matching row
            matching_rows = history_df[
                (history_df['Query'] == original_query) & 
                (history_df['Search Date'] + ' ' + history_df['Search Time'] == timestamp_part)
            ]
            
            if not matching_rows.empty:
                selected_row = matching_rows.iloc[0]
                s3_key = selected_row['S3 Key']
                s3_full_path = selected_row.get('S3 Full Path', f"s3://{config.bucket_name}/{s3_key}")
                bucket_name = selected_row.get('Bucket', config.bucket_name)
                
                st.markdown(f"### 📊 Dataset: {original_query}")
                st.caption(f"🕒 Created: {timestamp_part}")
            
            # Show metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Max Comments:** {selected_row['Max Comments']}")
            with col2:
                st.info(f"**Max Videos:** {selected_row['Max Videos']}")
            with col3:
                st.info(f"**S3 Path:** `{s3_full_path}`")
            
            try:
                with st.spinner("Loading dataset from S3..."):
                    # Use s3_full_path for easier access
                    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                    df_data = pickle.loads(response['Body'].read())
                    
                    st.success(f"✅ Loaded {len(df_data)} records")
                    
                    # Display stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Comments", len(df_data))
                    with col2:
                        avg_sentiment = df_data['sentiment_score'].mean() if 'sentiment_score' in df_data.columns else 0
                        st.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
                    with col3:
                        unique_videos = df_data['title'].nunique() if 'title' in df_data.columns else 0
                        st.metric("Unique Videos", unique_videos)
                    
                    # Display data
                    st.dataframe(
                        df_data, 
                        use_container_width=True,
                        height=400,
                        column_config={
                            "sentiment_score": st.column_config.NumberColumn("Sentiment", format="%.2f", width="small"),
                            "comment": st.column_config.TextColumn("Comment", width="large"),
                            "person": st.column_config.TextColumn("User", width="medium"),
                            "user_channel": st.column_config.LinkColumn("User Channel", width="medium"),
                            "title": st.column_config.TextColumn("Video", width="medium"),
                            "translated": st.column_config.TextColumn("Translation", width="large"),
                            "link": st.column_config.LinkColumn("Video Link", width="small"),
                            "normalized": None  # Hide this column
                        },
                        hide_index=True
                    )
                    
            except Exception as e:
                st.error(f"❌ Error loading dataset: {str(e)}")
                st.write("**Debug Info:**")
                st.write(f"- Bucket: {bucket_name}")
                st.write(f"- S3 Key: {s3_key}")
                st.write(f"- Full Path: {s3_full_path}")
                
                # Try with default credentials as fallback
                try:
                    fallback_s3 = boto3.client('s3')
                    response = fallback_s3.get_object(Bucket=bucket_name, Key=s3_key)
                    df_data = pickle.loads(response['Body'].read())
                    st.success(f"✅ Loaded with fallback: {len(df_data)} records")
                    st.dataframe(df_data, use_container_width=True, height=400)
                except Exception as fallback_error:
                    st.error(f"❌ Fallback also failed: {str(fallback_error)}")
    
    else:
        st.info("📭 No datasets found. Run some searches from the main page to populate data.")
        
except Exception as e:
    st.error(f"❌ Error accessing DynamoDB: {str(e)}")

# Credits
st.markdown("---")
st.markdown("**👨💻 Developed by Roberto Moreira Diniz**")
