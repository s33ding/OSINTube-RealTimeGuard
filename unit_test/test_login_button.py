import requests
import webbrowser
import time

def test_login_button_redirect():
    """Test the exact URL that the login button uses"""
    
    login_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email+openid+profile&redirect_uri=http://localhost:8501/callback"
    
    print("🔐 Testing Login with Google button...")
    print(f"URL: {login_url}")
    
    try:
        # Test the redirect chain
        response = requests.get(login_url, allow_redirects=False, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            google_url = response.headers.get('Location', '')
            print(f"Redirects to Google: {google_url[:100]}...")
            
            # Test Google's response
            google_response = requests.get(google_url, allow_redirects=False, timeout=10)
            print(f"Google Status: {google_response.status_code}")
            
            if google_response.status_code == 200:
                print("✅ Google OAuth page loads successfully!")
                print("🎯 Login button should work in browser")
                return True
            elif google_response.status_code == 302:
                google_redirect = google_response.headers.get('Location', '')
                if 'error' in google_redirect:
                    print(f"❌ Google OAuth error: {google_redirect}")
                    return False
                else:
                    print("✅ Google OAuth working (additional redirect)")
                    return True
            else:
                print(f"❌ Google OAuth issue: {google_response.status_code}")
                return False
        else:
            print(f"❌ Cognito issue: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def open_login_in_browser():
    """Open the login URL in browser for manual testing"""
    
    login_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email+openid+profile&redirect_uri=http://localhost:8501/callback"
    
    print("🌐 Opening login URL in browser...")
    print(f"URL: {login_url}")
    
    try:
        webbrowser.open(login_url)
        print("✅ Browser opened - test the login manually")
        return True
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"📋 Copy this URL to test manually: {login_url}")
        return False

if __name__ == "__main__":
    print("🧪 Testing 🔐 Login with Google button...")
    
    # Test the redirect programmatically
    result = test_login_button_redirect()
    
    if result:
        print("\n✅ Login button redirect is working!")
        print("🎯 The OAuth flow should work in the browser")
        
        # Optionally open in browser for manual test
        user_input = input("\n🌐 Open login in browser for manual test? (y/n): ")
        if user_input.lower() == 'y':
            open_login_in_browser()
    else:
        print("\n❌ Login button has issues")
        print("🔧 Check Google OAuth configuration")
