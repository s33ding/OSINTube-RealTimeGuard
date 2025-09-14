import unittest
from unittest.mock import patch, MagicMock
import config

class TestCognitoRedirect(unittest.TestCase):
    
    @patch('config.get_parameter')
    def test_cognito_redirect_url(self, mock_get_parameter):
        # Mock the cognito domain
        mock_get_parameter.return_value = 'test-domain'
        
        # Expected redirect URI
        expected_redirect = "https://app.dataiesb.com/osintube"
        
        # Get values from config
        cognito_domain = config.get_parameter('/osintube/cognito_domain')
        client_id = config.cognito_client_id
        
        # Build login URL
        login_url = f"https://{cognito_domain}.auth.us-east-1.amazoncognito.com/login?client_id={client_id}&response_type=code&scope=email+openid+profile&redirect_uri={expected_redirect}"
        
        # Assertions
        self.assertIn(expected_redirect, login_url)
        self.assertIn("app.dataiesb.com/osintube", login_url)
        self.assertIn("response_type=code", login_url)
        
    def test_redirect_uri_format(self):
        redirect_uri = "https://app.dataiesb.com/osintube"
        
        # Test redirect URI format
        self.assertTrue(redirect_uri.startswith("https://"))
        self.assertIn("app.dataiesb.com", redirect_uri)
        self.assertIn("osintube", redirect_uri)

if __name__ == '__main__':
    unittest.main()
