# Local testing configuration
import os

# Mock AWS parameters for local testing
LOCAL_MODE = os.getenv('LOCAL_MODE', 'true').lower() == 'true'

def get_parameter(param_name):
    """Mock parameter store for local testing"""
    mock_params = {
        '/osintube/cognito_domain': 'mock-domain',
        '/osintube/s3_bucket': 'mock-bucket',
        '/osintube/dynamodb_table': 'mock-table'
    }
    return mock_params.get(param_name, 'mock-value')

# Mock Cognito client ID
cognito_client_id = 'mock-client-id'
