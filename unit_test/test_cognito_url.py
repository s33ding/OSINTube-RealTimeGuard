import pytest
import requests

def test_cognito_oauth_url_direct():
    """Test Cognito OAuth URL directly"""
    
    oauth_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email+openid+profile&redirect_uri=http://localhost:8501/callback"
    
    try:
        response = requests.get(oauth_url, allow_redirects=False, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✅ Redirects to: {location}")
            
            if "accounts.google.com" in location:
                print("✅ Successfully redirects to Google OAuth")
                return True
            else:
                print(f"❌ Unexpected redirect: {location}")
                return False
                
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_google_oauth_response():
    """Test what Google returns"""
    
    # This is the URL Cognito redirects to
    google_url = "https://accounts.google.com/o/oauth2/v2/auth?client_id=71am2v0jcp9uqpihrh9hjqtp6o&redirect_uri=https%3A%2F%2Fosintube-w7p7627g.auth.us-east-1.amazoncognito.com%2Foauth2%2Fidpresponse&scope=email+openid+profile&response_type=code"
    
    try:
        response = requests.get(google_url, allow_redirects=False, timeout=10)
        print(f"Google OAuth Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Google OAuth page loads successfully")
            return True
        elif response.status_code == 302:
            print(f"Google redirects to: {response.headers.get('Location', '')}")
            return True
        else:
            print(f"❌ Google OAuth error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Google OAuth error: {e}")
        return False

def test_cognito_domain():
    """Test base Cognito domain"""
    
    domain = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com"
    
    try:
        response = requests.get(domain, timeout=10)
        print(f"Cognito domain status: {response.status_code}")
        
        if response.status_code in [200, 404]:  # 404 is normal for base domain
            print("✅ Cognito domain is accessible")
            return True
        else:
            print(f"❌ Cognito domain issue: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cognito domain error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Cognito OAuth URL...")
    
    result1 = test_cognito_oauth_url_direct()
    result2 = test_google_oauth_response()
    result3 = test_cognito_domain()
    
    if all([result1, result2, result3]):
        print("✅ All Cognito URL tests passed")
    else:
        print("❌ Some Cognito URL tests failed")
