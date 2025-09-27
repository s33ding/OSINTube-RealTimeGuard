import streamlit as st
import pandas as pd
import pickle
import pyfiglet
from shared_func.readonly_client import get_clients
from shared_func.sentiment_viz import create_sentiment_combined, create_sentiment_counts
from shared_func.llama_agent import analyze_dataset_with_llama, ask_dataset_question

st.set_page_config(page_title="Public Data", page_icon="🛡️", layout="wide")

# Public page - no authentication required

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
st.markdown('<div class="cyber-title">📊 Public Data</div>', unsafe_allow_html=True)

try:
    # Get clients
    s3_client, dynamodb_client = get_clients()
    
    if not s3_client or not dynamodb_client:
        st.error("❌ Failed to initialize clients")
        st.stop()
    
    # Get data from DynamoDB
    response = dynamodb_client.scan(TableName='osintube')
    items = response.get('Items', [])
    
    if not items:
        st.info("📭 No datasets found")
        st.stop()
    
    st.success(f"✅ Found {len(items)} datasets")
    
    # Create dataset options
    dataset_options = []
    for i, item in enumerate(items):
        query = item.get('video_query', {}).get('S', f'Dataset {i+1}')
        date = item.get('search_date', {}).get('S', '')
        comments = item.get('comments_found', {}).get('N', '0')
        dataset_options.append(f"{query} | {date} | {comments} comments")
    
    # Dataset selection
    selected_idx = st.selectbox("Select Dataset:", range(len(dataset_options)), 
                               format_func=lambda x: dataset_options[x])
    
    # Get selected dataset info
    item = items[selected_idx]
    s3_key = item.get('s3', {}).get('S', '')
    bucket_name = item.get('bucket_name', {}).get('S', 's33ding-osintube-w7p7627g')
    
    # Auto-load dataset when selection changes
    if 'current_selection' not in st.session_state or st.session_state.current_selection != selected_idx:
        st.session_state.current_selection = selected_idx
        try:
            with st.spinner("Loading dataset..."):
                response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                df_data = pickle.loads(response['Body'].read())
                
                # Store in session state
                st.session_state.df_data = df_data
                st.session_state.data_loaded = True
                st.session_state.current_s3_key = s3_key
                st.session_state.current_bucket = bucket_name
                st.session_state.current_item = item
                
                st.success(f"✅ Auto-loaded {len(df_data)} records")
        except Exception as e:
            st.error(f"❌ Auto-load error: {e}")
    
    # Display loaded data (always visible)
    if st.session_state.get('data_loaded', False):
        df_data = st.session_state.df_data
        
        # Filter visualization
        zero_count = (df_data['sentiment_score'] == 0).sum()
        total_count = len(df_data)
        zero_ratio = zero_count / total_count if total_count > 0 else 0
        
        # Basic metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📊 Records", len(df_data))
        with col2:
            avg_sentiment = df_data['sentiment_score'].mean() if 'sentiment_score' in df_data.columns else 0
            st.metric("😊 Avg Sentiment", f"{avg_sentiment:.2f}")
        with col3:
            unique_users = df_data['person'].nunique() if 'person' in df_data.columns else 0
            st.metric("👥 Users", unique_users)
        with col4:
            positive = (df_data['sentiment_score'] > 0).sum() if 'sentiment_score' in df_data.columns else 0
            st.metric("✅ Positive", positive)
        with col5:
            unique_videos = df_data['title'].nunique() if 'title' in df_data.columns else 0
            st.metric("🎥 Videos", unique_videos)
        
        # DataFrame display (reset index for clean 0,1,2... display)
        st.markdown("### 📋 Dataset View")
        display_df = df_data.reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True, height=700,
                    column_config={
                        "link": st.column_config.LinkColumn("🎥 Video", width="small"),
                        "user_channel": st.column_config.LinkColumn("📺 Channel", width="small"),
                        "comment": st.column_config.TextColumn("💬 Comment", width="large"),
                        "sentiment_score": st.column_config.NumberColumn("😊 Sentiment", width="small", format="%.2f"),
                        "person": st.column_config.TextColumn("👤 User", width="medium"),
                        "title": st.column_config.TextColumn("🎥 Title", width="medium")
                    })
        
        # Sentiment Analysis Charts
        st.markdown("### 📊 Sentiment Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            sentiment_fig = create_sentiment_combined(df_data)
            if sentiment_fig:
                st.plotly_chart(sentiment_fig, use_container_width=True)
        
        with col2:
            counts_fig = create_sentiment_counts(df_data)
            if counts_fig:
                st.plotly_chart(counts_fig, use_container_width=True)
    
    # Threat Analysis Agent (always visible after dataset selection)
    st.markdown("### 🤖 Threat Analysis Agent")
    if st.button("🔍 Analyze for Threats"):
        if st.session_state.get('data_loaded', False):
            df_data = st.session_state.df_data
            with st.spinner("🤖 AI Agent analyzing for threats..."):
                query = item.get('video_query', {}).get('S', 'Unknown query')
                result = analyze_dataset_with_llama(df_data, s3_key, bucket_name, query)
                
                if result['status'] == 'success':
                    st.success("✅ Threat analysis completed!")
                    
                    # Display HTML analysis with proper rendering
                    analysis = result['analysis']
                    st.markdown(analysis, unsafe_allow_html=True)
                    
                else:
                    st.error(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
        else:
            st.warning("⚠️ Please load a dataset first")

        # Q&A Section
        if df_data is not None and not df_data.empty:
            st.markdown("---")
            st.header("🔍 Ask Questions About This Dataset")
            
            # Quick question buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔥 Most Threatening Users"):
                    st.session_state.qa_question = "Who are the most threatening users and what did they say?"
            with col2:
                if st.button("📊 Sentiment Patterns"):
                    st.session_state.qa_question = "What are the main sentiment patterns and emotional themes?"
            with col3:
                if st.button("🎯 Key Topics"):
                    st.session_state.qa_question = "What are the main topics and concerns being discussed?"
            
            # Custom question input
            question = st.text_area(
                "Ask anything about this dataset:",
                value=st.session_state.get('qa_question', ''),
                placeholder="e.g., Are there any coordinated attacks? What users show concerning behavior?",
                height=80
            )
            
            if st.button("🚀 Analyze Question", type="primary"):
                if question.strip():
                    with st.spinner("🤖 AI is analyzing your question..."):
                        try:
                            result = ask_dataset_question(df_data, question, item.get('video_query', {}).get('S', ''))
                            
                            if result['status'] == 'success':
                                st.success("✅ Analysis Complete!")
                                st.markdown(result['response'], unsafe_allow_html=True)
                            else:
                                st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"❌ Q&A Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a question")
            
except Exception as e:
    st.error(f"❌ General error: {e}")
    import traceback
    st.code(traceback.format_exc())
