import streamlit as st

# Page config
st.set_page_config(
    page_title="WHOAMI - Roberto Moreira Diniz",
    page_icon="💀",
    layout="wide"
)

# TryHackMe style CSS
st.markdown("""
<style>
.stApp > header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.main .block-container {padding-top: 0rem;}

body {
    background: #212529;
    color: #ffffff;
}

.thm-header {
    background: linear-gradient(135deg, #212529 0%, #343a40 100%);
    padding: 2rem;
    border-radius: 10px;
    border: 2px solid #00d4aa;
    margin-bottom: 2rem;
    text-align: center;
}

.thm-title {
    font-family: 'Courier New', monospace;
    font-size: 3rem;
    font-weight: bold;
    color: #00d4aa;
    text-shadow: 0 0 20px #00d4aa;
    margin: 0;
}

.thm-subtitle {
    font-family: 'Courier New', monospace;
    color: #ffffff;
    font-size: 1.2rem;
    margin-top: 0.5rem;
}

.terminal-box {
    background: #1a1a1a;
    border: 2px solid #00d4aa;
    border-radius: 8px;
    padding: 1.5rem;
    font-family: 'Courier New', monospace;
    color: #00d4aa;
    margin: 1rem 0;
}

.prompt {
    color: #ff6b6b;
    font-weight: bold;
}

.output {
    color: #ffffff;
    margin-left: 1rem;
}

.thm-button {
    background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);
    color: #ffffff;
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    text-decoration: none;
    display: inline-block;
    margin: 1rem 0;
    transition: all 0.3s ease;
}

.thm-button:hover {
    background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
}

.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.skill-badge {
    background: #343a40;
    border: 1px solid #00d4aa;
    border-radius: 6px;
    padding: 0.5rem;
    text-align: center;
    color: #00d4aa;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="thm-header">
    <div class="thm-title">🥷🏿 WHOAMI 🥷🏿</div>
    <div class="thm-subtitle">DataOps Engineer & OSINT Enthusiast</div>
</div>
""", unsafe_allow_html=True)

# Terminal section
st.markdown("""
<div class="terminal-box">
<span class="prompt">root@osintube:~#</span> cat /etc/passwd | grep roberto<br>
<span class="output">roberto:x:1337:1337:DataOps Engineer:/home/roberto:/bin/bash</span><br><br>

<span class="prompt">root@osintube:~#</span> ls -la /projects/<br>
<span class="output">OSINTube-RealTimeGuard: Real-time YouTube threat detection using AWS AI services for monitoring digital spaces and sentiment analysis.</span><br><br>

<span class="prompt">root@osintube:~#</span> cat /skills/stack.txt<br>
<span class="output">AWS • Python • Data Pipelines • Container Orchestration • OSINT • Big Data</span>
</div>
""", unsafe_allow_html=True)

# Skills badges
st.markdown("""
<div class="skills-grid">
    <div class="skill-badge">📊 DataOps Engineer</div>
    <div class="skill-badge">🐍 Python Developer</div>
    <div class="skill-badge">🔄 Data Pipelines</div>
    <div class="skill-badge">🔍 OSINT Specialist</div>
    <div class="skill-badge">📈 Big Data Analytics</div>
    <div class="skill-badge">🚢 Container Orchestration</div>
    <div class="skill-badge">⚙️ DevOps</div>
</div>
""", unsafe_allow_html=True)

# Resume download
st.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <a href="https://robertomdiniz.s3.us-east-1.amazonaws.com/roberto-resume.pdf" 
       target="_blank" class="thm-button">
       📄 DOWNLOAD RESUME
    </a>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: #6c757d; font-family: 'Courier New', monospace;">
    🛡️ [SECURITY_LEVEL: MAXIMUM] 🛡️
</div>
""", unsafe_allow_html=True)
