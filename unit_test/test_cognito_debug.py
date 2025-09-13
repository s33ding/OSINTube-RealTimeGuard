import unittest
import requests
import json
from urllib.parse import urlparse, parse_qs

class TestCognitoOAuthDebug(unittest.TestCase):
    
    def setUp(self):
        """Set up test configuration"""
        self.cognito_domain = "osintube-w7p7627g.auth.us-east-1.amazoncognito.com"
        self.client_id = "3gqft9u0m22tlviqpgepumnm3m"
        self.redirect_uri = "http://localhost:8501/callback"
        self.google_client_id = "781293193566-s1e99d7eiqgdlgcudevuf8hjjre2ssrp.apps.googleusercontent.com"
    
    def test_cognito_oauth_url(self):
        """Test Cognito OAuth authorization URL"""
        oauth_url = f"https://{self.cognito_domain}/oauth2/authorize?identity_provider=Google&client_id={self.client_id}&response_type=code&scope=email%20openid%20profile&redirect_uri={self.redirect_uri}"
        
        response = requests.get(oauth_url, allow_redirects=False, timeout=10)
        
        self.assertEqual(response.status_code, 302, "Cognito should redirect to Google")
        
        location = response.headers.get('Location', '')
        self.assertIn('accounts.google.com', location, "Should redirect to Google OAuth")
        
        # Parse Google URL
        parsed_url = urlparse(location)
        query_params = parse_qs(parsed_url.query)
        
        self.assertIn('client_id', query_params, "Google URL should contain client_id")
        actual_client_id = query_params['client_id'][0]
        self.assertEqual(actual_client_id, self.google_client_id, f"Expected {self.google_client_id}, got {actual_client_id}")
        
        print(f"✅ Cognito OAuth URL working")
        print(f"   Redirects to: {location[:80]}...")
        print(f"   Google Client ID: {actual_client_id}")
    
    def test_google_oauth_client(self):
        """Test Google OAuth client validation"""
        google_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={self.google_client_id}&redirect_uri=https%3A%2F%2F{self.cognito_domain}%2Foauth2%2Fidpresponse&scope=email+openid+profile&response_type=code"
        
        response = requests.get(google_url, allow_redirects=False, timeout=10)
        
        if response.status_code == 200:
            print("✅ Google OAuth client valid")
        elif response.status_code == 302:
            location = response.headers.get('Location', '')
            if 'error' in location.lower():
                self.fail(f"Google OAuth error: {location}")
            else:
                print("✅ Google OAuth client working (redirects to login)")
        else:
            self.fail(f"Google OAuth client issue: {response.status_code}")
    
    def test_redirect_uri_configuration(self):
        """Test redirect URI configuration"""
        required_uris = [
            f"https://{self.cognito_domain}/oauth2/idpresponse",
            self.redirect_uri
        ]
        
        print("📋 Required redirect URIs in Google Cloud Console:")
        for uri in required_uris:
            print(f"   - {uri}")
        
        # Test if callback endpoint exists
        try:
            callback_response = requests.get(self.redirect_uri, timeout=5)
            if callback_response.status_code == 200:
                print("✅ Streamlit callback endpoint accessible")
            else:
                print(f"⚠️ Callback endpoint returned: {callback_response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Streamlit app not running on localhost:8501")
        except Exception as e:
            print(f"⚠️ Callback test error: {e}")
    
    def test_cognito_token_endpoint(self):
        """Test Cognito token endpoint accessibility"""
        token_url = f"https://{self.cognito_domain}/oauth2/token"
        
        # Test with invalid request to see if endpoint exists
        response = requests.post(token_url, data={'invalid': 'test'}, timeout=10)
        
        # Should return 400 (bad request) not 404 (not found)
        self.assertNotEqual(response.status_code, 404, "Token endpoint should exist")
        print(f"✅ Cognito token endpoint accessible (status: {response.status_code})")
    
    def test_full_oauth_flow_simulation(self):
        """Simulate the complete OAuth flow"""
        print("\n🔄 Simulating complete OAuth flow:")
        
        # Step 1: User clicks login button
        print("1. User clicks 'Login with Google'")
        oauth_url = f"https://{self.cognito_domain}/oauth2/authorize?identity_provider=Google&client_id={self.client_id}&response_type=code&scope=email%20openid%20profile&redirect_uri={self.redirect_uri}"
        
        # Step 2: Cognito redirects to Google
        response = requests.get(oauth_url, allow_redirects=False, timeout=10)
        self.assertEqual(response.status_code, 302)
        google_url = response.headers.get('Location', '')
        print("2. Cognito redirects to Google ✅")
        
        # Step 3: Check Google response
        google_response = requests.get(google_url, allow_redirects=False, timeout=10)
        if google_response.status_code in [200, 302]:
            location = google_response.headers.get('Location', '')
            if 'error' in location.lower():
                print(f"3. Google OAuth error: {location} ❌")
                self.fail("Google OAuth configuration issue")
            else:
                print("3. Google OAuth working ✅")
        
        print("4. User would authenticate with Google")
        print("5. Google would redirect back to Cognito")
        print("6. Cognito would redirect to callback with auth code")
        print("7. Callback would process authentication")

if __name__ == '__main__':
    unittest.main(verbosity=2)
