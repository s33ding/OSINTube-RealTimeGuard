import streamlit as st
import pyfiglet

st.set_page_config(page_title="Who Am I", page_icon="👤", layout="wide")

# Same CSS as other pages
st.markdown("""
<style>
.stApp > header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.main .block-container {padding-top: 0rem;}

.title-container {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3, #54a0ff);
    background-size: 400% 400%;
    animation: gradientShift 8s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    padding: 1rem;
    white-space: pre;
    font-size: 0.8rem;
    line-height: 1;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.cyber-title {
    font-family: 'Courier New', monospace;
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(45deg, #00d4aa, #00ff41);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 1rem 0;
    text-shadow: 0 0 20px rgba(0, 212, 170, 0.5);
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
</style>
""", unsafe_allow_html=True)

# Title section
st.markdown('<div class="cyber-title">Roberto Moreira Diniz</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size: 3rem; margin: 1rem 0;">🥷🏿</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #00d4aa; font-family: Courier New, monospace; font-size: 1.2rem; margin-bottom: 2rem;">DataOps Engineer & OSINT Enthusiast</div>', unsafe_allow_html=True)

# Terminal info
st.markdown("""
<div class="terminal-box">
<span style="color: #ff6b6b;">root@osintube:~#</span> whoami<br>
<span style="color: #ffffff;">roberto:x:1337:1337:DataOps Engineer:/home/roberto:/bin/bash</span><br><br>

<span style="color: #ff6b6b;">root@osintube:~#</span> cat /about/me.txt<br>
<span style="color: #ffffff;">Passionate DataOps Engineer specializing in OSINT and threat detection systems. Expert in building real-time data pipelines and AI-powered security analytics using AWS cloud infrastructure.</span><br><br>

<span style="color: #ff6b6b;">root@osintube:~#</span> cat /projects/current.txt<br>
<span style="color: #ffffff;">OSINTube-RealTimeGuard is an advanced OSINT (Open Source Intelligence) platform that monitors YouTube content in real-time to detect potential security threats, hate speech, and suspicious activities. Built with AWS cloud infrastructure and powered by LLaMA AI.</span><br><br>

<span style="color: #ff6b6b;">root@osintube:~#</span> cat /skills/stack.txt<br>
<span style="color: #ffffff;">AWS • Python • Streamlit • Docker • Terraform • DynamoDB • S3 • Bedrock • LLaMA • OSINT • Threat Detection • Data Pipelines • DevOps</span>
</div>
""", unsafe_allow_html=True)

# Link to resume page
st.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <a href="https://robertomdiniz.s3.us-east-1.amazonaws.com/roberto-resume.pdf" 
       target="_blank" 
       style="background: #00d4aa; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-family: 'Courier New', monospace; font-weight: bold;">
       📄 View Full Resume
    </a>
</div>
""", unsafe_allow_html=True)
