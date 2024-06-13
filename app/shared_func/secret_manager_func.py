import boto3
import json

def get_secret(secret_name, session):
    """
    Retrieves the value of the specified AWS Secrets Manager secret using the provided session object
    
    Args:
    - secret_name (str): the name of the AWS Secrets Manager secret to retrieve
    - session (boto3.Session): the session object for initializing the Secrets Manager client
    
    Returns:
    - dct (dict): a dictionary containing the values in the specified secret
    """
    # Initialize the Secrets Manager client using the session
    client = session.client('secretsmanager')
    
    # Use Secrets Manager client object to get secret value
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    
    # Extract the values from the secret
    dct = json.loads(get_secret_value_response['SecretString'])
    
    return dct

