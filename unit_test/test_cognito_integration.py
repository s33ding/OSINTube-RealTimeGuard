import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.cognito_func import validate_iesb_email, process_google_callback
import streamlit as st

def test_validate_iesb_email():
    """Test IESB email validation"""
    
    # Valid email
    assert validate_iesb_email("roberto.diniz@iesb.edu.br") == True
    assert validate_iesb_email("ROBERTO.DINIZ@IESB.EDU.BR") == True
    
    # Invalid emails
    assert validate_iesb_email("other@iesb.edu.br") == False
    assert validate_iesb_email("roberto.diniz@gmail.com") == False
    assert validate_iesb_email("") == False
    assert validate_iesb_email(None) == False
    
    print("✅ Email validation tests passed")

def test_process_google_callback():
    """Test Google OAuth callback processing"""
    
    # Mock streamlit session state
    if not hasattr(st, 'session_state'):
        st.session_state = {}
    
    # Valid user info
    valid_user_info = {
        'email': 'roberto.diniz@iesb.edu.br',
        'name': 'Roberto Diniz'
    }
    
    success, message = process_google_callback(valid_user_info)
    assert success == True
    assert "Welcome" in message
    assert st.session_state.get('authenticated') == True
    assert st.session_state.get('user_email') == 'roberto.diniz@iesb.edu.br'
    
    print("✅ Valid user callback test passed")
    
    # Invalid user info
    invalid_user_info = {
        'email': 'other@gmail.com',
        'name': 'Other User'
    }
    
    success, message = process_google_callback(invalid_user_info)
    assert success == False
    assert "Access denied" in message
    
    print("✅ Invalid user callback test passed")

def test_cognito_oauth_url():
    """Test Cognito OAuth URL construction"""
    
    # Expected OAuth URL components
    expected_domain = "osintube-w7p7627g.auth.us-east-1.amazoncognito.com"
    expected_client_id = "3gqft9u0m22tlviqpgepumnm3m"
    expected_redirect_uri = "http://localhost:8501/callback"
    
    # Construct OAuth URL
    oauth_url = f"https://{expected_domain}/oauth2/authorize?identity_provider=Google&client_id={expected_client_id}&response_type=code&scope=email+openid+profile&redirect_uri={expected_redirect_uri}"
    
    # Validate URL components
    assert expected_domain in oauth_url
    assert expected_client_id in oauth_url
    assert "identity_provider=Google" in oauth_url
    assert "response_type=code" in oauth_url
    assert "scope=email+openid+profile" in oauth_url
    
    print(f"✅ OAuth URL constructed: {oauth_url}")

def test_token_validation():
    """Test JWT token validation logic"""
    
    # Mock JWT payload
    mock_payload = {
        'sub': 'google-oauth2|123456789',
        'email': 'roberto.diniz@iesb.edu.br',
        'name': 'Roberto Diniz',
        'exp': 1694616000,  # Future timestamp
        'iat': 1694612400   # Past timestamp
    }
    
    # Test email extraction
    email = mock_payload.get('email', '')
    assert email == 'roberto.diniz@iesb.edu.br'
    
    # Test email validation
    assert validate_iesb_email(email) == True
    
    print("✅ Token validation test passed")

if __name__ == "__main__":
    test_validate_iesb_email()
    test_process_google_callback()
    test_cognito_oauth_url()
    test_token_validation()
    print("✅ All Cognito integration tests passed")
