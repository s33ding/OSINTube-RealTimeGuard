import streamlit as st

st.set_page_config(page_title="Login Success", page_icon="✅")

# Get OAuth parameters
query_params = st.query_params
auth_code = query_params.get('code')
error = query_params.get('error')

if error:
    st.error(f"❌ OAuth Error: {error}")
    error_description = query_params.get('error_description', '')
    if error_description:
        st.error(f"Description: {error_description}")
    
    if st.button("🔙 Back to Login"):
        st.switch_page("🏠_Home.py")
    st.stop()

if auth_code:
    st.title("✅ Login Successful!")
    
    # Store authentication in session
    st.session_state.authenticated = True
    st.session_state.user_email = 'roberto.diniz@iesb.edu.br'
    
    st.success("Welcome roberto.diniz@iesb.edu.br!")
    st.info("You can now access OSINTube features.")
    
    if st.button("🏠 Go to Home"):
        st.switch_page("🏠_Home.py")
else:
    st.warning("⚠️ No authorization code received")
    if st.button("🔙 Try Again"):
        st.switch_page("🏠_Home.py")
