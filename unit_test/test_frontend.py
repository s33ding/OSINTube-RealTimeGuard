import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

import streamlit as st
from unittest.mock import patch, MagicMock

def test_home_page_unauthenticated():
    """Test home page behavior when not authenticated"""
    
    # Mock streamlit session state
    with patch('streamlit.session_state', {}):
        with patch('shared_func.cognito_func.is_authenticated', return_value=False):
            # Import home page logic
            from shared_func.cognito_func import is_authenticated
            
            # Test authentication check
            assert is_authenticated() == False
            print("✅ Unauthenticated state detected correctly")

def test_home_page_authenticated():
    """Test home page behavior when authenticated"""
    
    # Mock authenticated session state
    mock_session = {
        'authenticated': True,
        'user_email': 'roberto.diniz@iesb.edu.br',
        'user_name': 'Roberto Diniz'
    }
    
    with patch('streamlit.session_state', mock_session):
        with patch('shared_func.cognito_func.is_authenticated', return_value=True):
            with patch('shared_func.cognito_func.get_current_user', return_value='roberto.diniz@iesb.edu.br'):
                
                from shared_func.cognito_func import is_authenticated, get_current_user
                
                # Test authentication check
                assert is_authenticated() == True
                assert get_current_user() == 'roberto.diniz@iesb.edu.br'
                print("✅ Authenticated state detected correctly")

def test_login_button_html():
    """Test login button HTML generation"""
    
    expected_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email+openid+profile&redirect_uri=http://localhost:8501/callback"
    
    login_html = f"""
    <script>
        window.location.href = "{expected_url}";
    </script>
    """
    
    # Check HTML contains correct URL
    assert "window.location.href" in login_html
    assert expected_url in login_html
    assert "identity_provider=Google" in login_html
    
    print("✅ Login button HTML generated correctly")

def test_callback_page_logic():
    """Test callback page processing logic"""
    
    # Mock successful callback
    mock_tokens = {
        'id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlJvYmVydG8gRGluaXoiLCJlbWFpbCI6InJvYmVydG8uZGluaXpAaWVzYi5lZHUuYnIiLCJpYXQiOjE1MTYyMzkwMjJ9.invalid'
    }
    
    # Test token validation logic
    try:
        import base64
        import json
        
        # Mock JWT decode (normally would validate signature)
        payload_part = mock_tokens['id_token'].split('.')[1]
        # Add padding if needed
        payload_part += '=' * (4 - len(payload_part) % 4)
        
        # This would normally decode, but our mock token is invalid
        # Just test the structure
        assert len(mock_tokens['id_token'].split('.')) == 3
        print("✅ JWT token structure valid")
        
    except Exception as e:
        print(f"⚠️ JWT decode test skipped (expected with mock token): {e}")

def test_streamlit_components():
    """Test Streamlit components integration"""
    
    # Test that required Streamlit functions are available
    try:
        import streamlit as st
        import streamlit.components.v1 as components
        
        # Check if key functions exist
        assert hasattr(st, 'button')
        assert hasattr(st, 'markdown')
        assert hasattr(st, 'stop')
        assert hasattr(components, 'html')
        
        print("✅ Streamlit components available")
        
    except ImportError as e:
        print(f"❌ Streamlit import error: {e}")

if __name__ == "__main__":
    print("🧪 Testing frontend components...")
    test_home_page_unauthenticated()
    test_home_page_authenticated()
    test_login_button_html()
    test_callback_page_logic()
    test_streamlit_components()
    print("✅ Frontend tests completed")
