import requests
import time

def test_google_client_validation():
    """Test Google OAuth client validation"""
    
    client_id = "71am2v0jcp9uqpihrh9hjqtp6o"
    
    # Test with a simple validation URL
    validation_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&scope=email"
    
    try:
        response = requests.get(validation_url, allow_redirects=False, timeout=10)
        print(f"Google client validation status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if 'error' in location:
                print(f"❌ Client validation failed: {location}")
                return False
            else:
                print(f"✅ Client exists and is valid")
                return True
        elif response.status_code == 200:
            print("✅ Client validation successful")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating client: {e}")
        return False

def test_dataiesb_oauth():
    """Test if Data-IESB OAuth works with same client"""
    
    dataiesb_url = "https://auth.dataiesb.com/oauth2/authorize?client_id=71am2v0jcp9uqpihrh9hjqtp6o&response_type=code&scope=email+openid&redirect_uri=https://dataiesb.com/callback.html"
    
    try:
        response = requests.get(dataiesb_url, allow_redirects=False, timeout=10)
        print(f"Data-IESB OAuth status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if 'accounts.google.com' in location and 'error' not in location:
                print("✅ Data-IESB OAuth works correctly")
                return True
            else:
                print(f"❌ Data-IESB OAuth issue: {location}")
                return False
        else:
            print(f"❌ Data-IESB OAuth unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Data-IESB OAuth error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Google OAuth client...")
    
    result1 = test_google_client_validation()
    result2 = test_dataiesb_oauth()
    
    if result1 and result2:
        print("✅ Google OAuth client is working")
        print("⚠️ The issue might be with redirect URI propagation delay")
        print("💡 Try the OAuth flow in a browser - it might work now")
    else:
        print("❌ Google OAuth client has issues")
        print("🔧 Check Google Cloud Console configuration")
