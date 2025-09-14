import streamlit as st
import requests
import base64
import json
import config
import os

def handle_oauth_callback():
    """Handle OAuth callback from Cognito"""
    query_params = st.query_params
    
    if 'code' in query_params:
        auth_code = query_params['code']
        
        # Exchange authorization code for tokens
        token_url = f"https://{config.get_parameter('/osintube/cognito_domain')}.auth.us-east-1.amazoncognito.com/oauth2/token"
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': config.cognito_client_id,
            'code': auth_code,
            'redirect_uri': 'https://app.dataiesb.com/osintube'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            id_token = tokens.get('id_token')
            
            if id_token:
                # Decode JWT payload (without verification for simplicity)
                payload = id_token.split('.')[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = json.loads(base64.b64decode(payload))
                
                user_email = decoded.get('email')
                
                # Only allow roberto.diniz@iesb.edu.br
                if user_email == 'roberto.diniz@iesb.edu.br':
                    st.session_state.authenticated = True
                    st.session_state.user_email = user_email
                    st.session_state.id_token = id_token
                    st.rerun()
                else:
                    st.error("❌ Access denied. Only roberto.diniz@iesb.edu.br is authorized.")
                    st.stop()

def is_authenticated():
    """Check if user is authenticated"""
    # Handle OAuth callback first
    handle_oauth_callback()
    
    return st.session_state.get('authenticated', False) and st.session_state.get('user_email') == 'roberto.diniz@iesb.edu.br'

def get_current_user():
    """Get current user email"""
    if is_authenticated():
        return st.session_state.get('user_email')
    return None

def logout_user():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.id_token = None
    
    logout_url = f"https://{config.get_parameter('/osintube/cognito_domain')}.auth.us-east-1.amazoncognito.com/logout?client_id={config.cognito_client_id}&logout_uri=https://app.dataiesb.com/osintube"
    st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)
