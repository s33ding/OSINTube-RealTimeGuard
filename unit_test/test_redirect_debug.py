import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

import requests

def test_cognito_oauth_url():
    """Test if Cognito OAuth URL is accessible"""
    
    oauth_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email+openid+profile&redirect_uri=http://localhost:8501/callback"
    
    try:
        # Test if URL is reachable
        response = requests.get(oauth_url, allow_redirects=False, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"✅ Redirect to: {response.headers.get('Location')}")
        elif response.status_code == 200:
            print("✅ OAuth URL is accessible")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing OAuth URL: {e}")

def test_google_oauth_client():
    """Test Google OAuth client configuration"""
    
    # Test if the client ID exists in Google
    client_id = "71am2v0jcp9uqpihrh9hjqtp6o"
    
    # This would normally require Google API, but we can check basic format
    assert len(client_id) > 10
    assert client_id.isalnum()
    
    print(f"✅ Google Client ID format valid: {client_id}")

def test_redirect_uri_format():
    """Test redirect URI format"""
    
    redirect_uri = "http://localhost:8501/callback"
    callback_uri = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/idpresponse"
    
    # Check if URIs are properly formatted
    assert redirect_uri.startswith("http")
    assert callback_uri.startswith("https")
    assert "/callback" in redirect_uri
    assert "/oauth2/idpresponse" in callback_uri
    
    print(f"✅ Redirect URI: {redirect_uri}")
    print(f"✅ Callback URI: {callback_uri}")

def test_cognito_domain():
    """Test Cognito domain accessibility"""
    
    domain = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com"
    
    try:
        response = requests.get(domain, timeout=10)
        print(f"Cognito domain status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Cognito domain is accessible")
        else:
            print(f"⚠️ Cognito domain returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing Cognito domain: {e}")

if __name__ == "__main__":
    print("🔍 Debugging OAuth redirect issues...")
    test_cognito_oauth_url()
    test_google_oauth_client()
    test_redirect_uri_format()
    test_cognito_domain()
    print("✅ Debug tests completed")
