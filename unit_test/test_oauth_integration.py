import requests
import json

def test_cognito_oauth_flow():
    """Test the complete OAuth integration flow"""
    
    print("🧪 Testing OSINTube OAuth Integration")
    print("=" * 50)
    
    # Step 1: Test Cognito OAuth URL
    print("1️⃣ Testing Cognito OAuth URL...")
    cognito_url = "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&client_id=3gqft9u0m22tlviqpgepumnm3m&response_type=code&scope=email%20openid%20profile&redirect_uri=http%3A//localhost%3A8501/callback"
    
    try:
        response = requests.get(cognito_url, allow_redirects=False, timeout=10)
        if response.status_code == 302:
            google_url = response.headers.get('Location', '')
            print(f"✅ Cognito redirects correctly")
            print(f"   Redirect URL: {google_url[:80]}...")
            
            # Extract Google client ID from redirect
            if "client_id=" in google_url:
                client_start = google_url.find("client_id=") + 10
                client_end = google_url.find("&", client_start)
                if client_end == -1:
                    client_end = len(google_url)
                actual_client = google_url[client_start:client_end]
                print(f"   Google Client ID: {actual_client}")
                
                # Step 2: Test Google OAuth client
                print("\n2️⃣ Testing Google OAuth Client...")
                google_test_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={actual_client}&redirect_uri=https%3A%2F%2Fosintube-w7p7627g.auth.us-east-1.amazoncognito.com%2Foauth2%2Fidpresponse&scope=email+openid+profile&response_type=code"
                
                google_response = requests.get(google_test_url, allow_redirects=False, timeout=10)
                
                if google_response.status_code == 200:
                    print("✅ Google OAuth client is valid and accessible")
                elif google_response.status_code == 302:
                    location = google_response.headers.get('Location', '')
                    if 'error' in location.lower():
                        print(f"❌ Google OAuth error: {location}")
                        if 'invalid_client' in location:
                            print("   Issue: Client ID not found in Google Cloud Console")
                        elif 'redirect_uri_mismatch' in location:
                            print("   Issue: Redirect URI not authorized")
                    else:
                        print("✅ Google OAuth client working (redirect to login)")
                else:
                    print(f"❌ Google OAuth client issue: {google_response.status_code}")
                
                # Step 3: Test redirect URI configuration
                print("\n3️⃣ Testing Redirect URI Configuration...")
                required_uris = [
                    "https://osintube-w7p7627g.auth.us-east-1.amazoncognito.com/oauth2/idpresponse",
                    "http://localhost:8501/callback"
                ]
                
                print("   Required redirect URIs in Google Cloud Console:")
                for uri in required_uris:
                    print(f"   - {uri}")
                
                # Step 4: Test Streamlit callback endpoint
                print("\n4️⃣ Testing Streamlit Callback Endpoint...")
                callback_url = "http://localhost:8501/callback"
                try:
                    callback_response = requests.get(callback_url, timeout=5)
                    if callback_response.status_code == 200:
                        print("✅ Streamlit callback endpoint accessible")
                    else:
                        print(f"⚠️ Streamlit callback returned: {callback_response.status_code}")
                except requests.exceptions.ConnectionError:
                    print("⚠️ Streamlit app not running on localhost:8501")
                except Exception as e:
                    print(f"⚠️ Callback test error: {e}")
                
            else:
                print("❌ Could not extract client ID from redirect")
        else:
            print(f"❌ Cognito OAuth failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cognito test error: {e}")
    
    # Step 5: Integration Summary
    print("\n" + "=" * 50)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print("✅ If all tests pass: OAuth flow should work")
    print("❌ If Google client fails: Add redirect URIs to Google Cloud Console")
    print("⚠️ If Streamlit not running: Start the app with 'streamlit run 🏠_Home.py'")
    print("\n🔧 Next steps:")
    print("1. Ensure Google OAuth client exists and has correct redirect URIs")
    print("2. Start Streamlit app if not running")
    print("3. Test login flow in browser")

if __name__ == "__main__":
    test_cognito_oauth_flow()
