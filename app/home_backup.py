import pandas as pd
import streamlit as st
from shared_func.main_func import extract_data
import config
from shared_func.s3_objects import *
from shared_func.dynamodb_func import log_search_to_dynamodb
from shared_func.cognito_func import is_authenticated, get_current_user, logout_user
import pyfiglet

# Handle OAuth callback
query_params = st.query_params
auth_code = query_params.get('code')
if auth_code:
    st.session_state.authenticated = True
    st.session_state.user_email = 'roberto.diniz@iesb.edu.br'
    st.rerun()

# OSINTube-RealTimeGuard Home Page
# Page config is handled by the main page file

# Hide Streamlit header and footer
st.markdown("""
<style>
/* Hide all Streamlit branding and headers */
.stApp > header {visibility: hidden !important; height: 0px !important;}
.stApp > div:first-child {visibility: hidden !important; height: 0px !important;}
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}

/* Remove top padding */
.main .block-container {padding-top: 0rem !important;}
.stApp {margin-top: -80px !important;}

/* Hide toolbar */
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}

/* Force hide any purple elements */
div[style*="background-color: rgb(240, 242, 246)"] {display: none !important;}
div[style*="background: rgb(240, 242, 246)"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Custom CSS and JavaScript for enhanced UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

.main-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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
    text-shadow: 0 0 20px rgba(255,255,255,0.5);
}

.cyber-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.5rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(45deg, #00ff41, #0080ff, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(0,255,65,0.7);
    animation: pulse 2s infinite;
    margin: 1rem 0;
}

.stats-card {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    transition: transform 0.3s ease;
}

.stats-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
}

.threat-meter {
    width: 100%;
    height: 20px;
    background: linear-gradient(90deg, #00ff00 0%, #ffff00 50%, #ff0000 100%);
    border-radius: 10px;
    position: relative;
    overflow: hidden;
}

.threat-indicator {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 30%;
    background: rgba(255,255,255,0.8);
    border-radius: 10px;
    animation: scan 2s linear infinite;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes pulse {
    0% { text-shadow: 0 0 30px rgba(0,255,65,0.7); }
    50% { text-shadow: 0 0 50px rgba(0,255,65,1), 0 0 80px rgba(0,128,255,0.8); }
    100% { text-shadow: 0 0 30px rgba(0,255,65,0.7); }
}

@keyframes scan {
    0% { left: -30%; }
    100% { left: 100%; }
}

.matrix-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    opacity: 0.1;
}
</style>

<script>
// Matrix rain effect
function createMatrixRain() {
    const canvas = document.createElement('canvas');
    canvas.className = 'matrix-bg';
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    const charArray = chars.split('');
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = Array(Math.floor(columns)).fill(1);
    
    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#00ff41';
        ctx.font = fontSize + 'px monospace';
        
        for (let i = 0; i < drops.length; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }
    
    setInterval(draw, 50);
}

// Particle system
function createParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.style.position = 'fixed';
    particleContainer.style.top = '0';
    particleContainer.style.left = '0';
    particleContainer.style.width = '100%';
    particleContainer.style.height = '100%';
    particleContainer.style.pointerEvents = 'none';
    particleContainer.style.zIndex = '-1';
    document.body.appendChild(particleContainer);
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '2px';
        particle.style.height = '2px';
        particle.style.background = '#00ff41';
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animation = `float ${3 + Math.random() * 4}s ease-in-out infinite`;
        particleContainer.appendChild(particle);
    }
}

// Initialize effects when page loads
setTimeout(() => {
    createMatrixRain();
    createParticles();
}, 1000);
</script>

<style>
@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
    50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Check authentication - redirect to Cognito if not authenticated  
if not is_authenticated():
    # Hide sidebar for login page
    st.markdown("""
    <style>
        .css-1d391kg {display: none}
        .css-1rs6os {display: none}
        .css-17eq0hr {display: none}
        [data-testid="stSidebar"] {display: none}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("# 🔐 OSINTube Login")
    st.markdown("### Real-Time Threat Detection System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Use Cognito app client ID (correct approach)
        oauth_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email+openid&redirect_uri=http://localhost:8501"
        
        st.link_button("🔐 Login with Google", oauth_url, type="primary", use_container_width=True)
        
        st.markdown("---")
        if st.button("📊 View Public Data", type="secondary", use_container_width=True):
            st.switch_page("pages/1_📊_Public_Data.py")
        
        st.info("Only roberto.diniz@iesb.edu.br can access this system")
    
    st.stop()

# Show current user and logout option
col1, col2 = st.columns([3, 1])
with col1:
    st.success(f"✅ Logged in as: {get_current_user()}")
with col2:
    if st.button("🚪 Logout", type="secondary"):
        logout_user()
        st.rerun()

# Create fancy ASCII title
ascii_title = pyfiglet.figlet_format('OSINTube', font='big')

# Main container
st.markdown(f'<div class="title-container">{ascii_title}</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-title">🛡️ REAL-TIME GUARD 🛡️</div>', unsafe_allow_html=True)

# Stats dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stats-card">
        <h3>🎯 Threat Level</h3>
        <div class="threat-meter">
            <div class="threat-indicator"></div>
        </div>
        <p>System Status: <span style="color: #00ff41;">ACTIVE</span></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stats-card">
        <h3>📊 Analysis Engine</h3>
        <p>Model: <span style="color: #0080ff;">Llama 4 Scout</span></p>
        <p>Provider: <span style="color: #ff6b6b;">AWS Bedrock</span></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stats-card">
        <h3>🌐 Data Sources</h3>
        <p>YouTube API: <span style="color: #00ff41;">✓ Connected</span></p>
        <p>AWS Translate: <span style="color: #00ff41;">✓ Ready</span></p>
    </div>
    """, unsafe_allow_html=True)

# Configuration values
st.markdown("### ⚙️ Configuration")
col1, col2 = st.columns(2)
with col1:
    comments_maxResult = st.number_input("Max Comments per Video", min_value=10, max_value=200, value=10, step=10)
with col2:
    search_limit = st.number_input("Max Videos to Search", min_value=1, max_value=20, value=1, step=1)

# Update config dynamically
config.comments_maxResult = comments_maxResult
config.search_limit = search_limit


# Display the README with animation instead of image
st.markdown("""
<div class="readme-container">
    <div class="animated-shield">🛡️</div>
    <div class="readme-text">
        <h3>🔍 Advanced Threat Detection System</h3>
        <p>OSINTube-RealTimeGuard is a cutting-edge real-time threat detection system for YouTube content. 
        It ensures online safety by identifying potential threats and suspicious activities through continuous 
        monitoring and analysis using state-of-the-art AI technology.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.readme-container {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem 0;
    position: relative;
    overflow: hidden;
}

.readme-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(0,255,65,0.1), transparent);
    animation: scan-line 4s linear infinite;
}

.animated-shield {
    font-size: 4rem;
    text-align: center;
    animation: shield-pulse 2s ease-in-out infinite;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 20px rgba(0,255,65,0.8));
}

.readme-text h3 {
    color: #00ff41;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 0 0 10px rgba(0,255,65,0.5);
}

.readme-text p {
    color: rgba(255,255,255,0.9);
    line-height: 1.6;
    text-align: center;
    margin-bottom: 2rem;
}

.tech-stack {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
}

.tech-badge {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: bold;
    animation: badge-glow 3s ease-in-out infinite;
    border: 1px solid rgba(255,255,255,0.2);
}

@keyframes shield-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

@keyframes scan-line {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

@keyframes badge-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(102,126,234,0.5); }
    50% { box-shadow: 0 0 20px rgba(102,126,234,0.8), 0 0 30px rgba(118,75,162,0.6); }
}
</style>
""", unsafe_allow_html=True)

# Input section
st.markdown("### 🔍 Threat Analysis")
st.write(f"**Example search:** 'Raça Rubro-Negra Força Jovem'")

# Create columns for input and buttons
col1, col2, col3 = st.columns([6, 1.5, 1.5])
with col1:
    input_data = st.text_input("Enter YouTube search query:", placeholder="Type your search term here...")
with col2:
    st.write("")  # Empty space for alignment
    run_button = st.button("▶️ Run", type="primary", use_container_width=True)
with col3:
    st.write("")  # Empty space for alignment
    stop_button = st.button("🛑 Stop", type="secondary", use_container_width=True)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False

# Handle stop button
if stop_button:
    st.session_state.stop_requested = True
    st.session_state.processing = False
    st.warning("⏹️ Process stopped by user")

# Credits section
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 15px; margin-top: 2rem;">
    <h4 style="color: #00ff41; margin-bottom: 1rem;">👨‍💻 Developed by</h4>
    <p style="font-size: 1.2rem; color: rgba(255,255,255,0.9); margin-bottom: 0.5rem;">
        <strong>Roberto Moreira Diniz</strong>
    </p>
    <p style="color: #4ecdc4; margin-bottom: 1rem;">DataOps Engineer</p>
    <a href="https://robertomdiniz.s3.amazonaws.com/roberto-resume.pdf" target="_blank" 
       style="color: #ff6b6b; text-decoration: none; font-weight: bold; 
              background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
              padding: 0.5rem 1rem; border-radius: 25px; 
              border: 1px solid rgba(255,255,255,0.2);">
        📄 View Resume
    </a>
</div>
""", unsafe_allow_html=True)

# Display the input value when the user presses run button or enters text
if (run_button or input_data) and input_data and not st.session_state.stop_requested:
    st.session_state.processing = True
    
    with st.spinner('🔍 Analyzing YouTube content...'):
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            if st.session_state.stop_requested:
                raise Exception("Process stopped by user")
                
            status_text.text('🎥 Searching YouTube videos...')
            progress_bar.progress(20)
            
            df = extract_data(input_data, search_limit, comments_maxResult)
            
            if st.session_state.stop_requested:
                raise Exception("Process stopped by user")
                
            status_text.text('💬 Processing comments...')
            progress_bar.progress(60)
            
            status_text.text('🤖 AI analysis in progress...')
            progress_bar.progress(80)
            
            key_word = normalize_key_name(input_data)
            
            if st.session_state.stop_requested:
                raise Exception("Process stopped by user")
                
            status_text.text('✅ Analysis complete!')
            progress_bar.progress(100)
            
            # Display results
            st.success(f"✅ Found {len(df)} comments for analysis")
            st.dataframe(df, use_container_width=True)
            
            # Upload to S3
            s3_key = f"dataset/{key_word}/{config.default_file_name}"
            upload_dataframe_to_s3(
                dataframe=df, 
                bucket_name=config.bucket_name, 
                key_name=s3_key, 
                path=config.output_path, 
                delete=config.delete_file
            )
            st.info("📤 Results uploaded to S3")
            
            # Log to DynamoDB
            video_title = video_info.get('title', 'Unknown')
            if log_search_to_dynamodb(input_data, s3_key, comments_maxResult, search_limit, video_title):
                st.success("📝 Search logged to history")
            else:
                st.warning("⚠️ Failed to log search history")
            
        except Exception as e:
            if "stopped by user" in str(e):
                st.warning("⏹️ Analysis stopped by user")
            else:
                st.error(f"❌ Error: {str(e)}")
        finally:
            # Clear progress indicators and reset state
            progress_bar.empty()
            status_text.empty()
            st.session_state.processing = False

# Reset stop state when input changes
if input_data != st.session_state.get('last_input', ''):
    st.session_state.stop_requested = False
    st.session_state.last_input = input_data
   

