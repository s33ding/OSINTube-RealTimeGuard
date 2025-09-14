#!/usr/bin/env python3
import subprocess
import boto3
import os

def deploy_docker_locally():
    """Deploy Docker container locally using ECR image with pod identity role"""
    # Cleanup existing containers
    subprocess.run(["docker", "stop", "osintube-local"], capture_output=True)
    subprocess.run(["docker", "rm", "osintube-local"], capture_output=True)
    
    # Remove unnamed osintube containers
    result = subprocess.run(["docker", "ps", "-a", "--filter", "ancestor=osintube", "--format", "{{.ID}}"], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        container_ids = result.stdout.strip().split('\n')
        for cid in container_ids:
            subprocess.run(["docker", "rm", "-f", cid], capture_output=True)
    
    # Use default AWS session to assume role
    session = boto3.Session()
    sts = session.client('sts', region_name='us-east-1')
    
    # Get account ID
    account_id = sts.get_caller_identity()['Account']
    role_arn = f"arn:aws:iam::{account_id}:role/osintube-readonly-role"
    
    # Assume the pod identity role
    credentials = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName='osintube-local-deploy'
    )['Credentials']
    
    # Set temporary AWS credentials as environment variables
    env = os.environ.copy()
    env.update({
        'AWS_ACCESS_KEY_ID': credentials['AccessKeyId'],
        'AWS_SECRET_ACCESS_KEY': credentials['SecretAccessKey'],
        'AWS_SESSION_TOKEN': credentials['SessionToken'],
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    
    # Get ECR repository URL
    result = subprocess.run([
        "aws", "ssm", "get-parameter", 
        "--name", "/osintube/ecr_repository_uri",
        "--query", "Parameter.Value",
        "--output", "text"
    ], capture_output=True, text=True, check=True, env=env)
    
    ecr_url = result.stdout.strip()
    
    # Login to ECR
    login_cmd = subprocess.run([
        "aws", "ecr", "get-login-password"
    ], capture_output=True, text=True, check=True, env=env)
    
    subprocess.run([
        "docker", "login", "--username", "AWS", 
        "--password-stdin", ecr_url.split('/')[0]
    ], input=login_cmd.stdout, text=True, check=True)
    
    # Pull and run container
    subprocess.run(["docker", "pull", f"{ecr_url}:latest"], check=True)
    subprocess.run([
        "docker", "run", "-d",
        "--name", "osintube-local", 
        "-p", "8501:8501",
        "-e", "BASE_URL_PATH=",
        "-e", "BROWSER_SERVER_ADDRESS=localhost",
        "-e", f"AWS_ACCESS_KEY_ID={credentials['AccessKeyId']}",
        "-e", f"AWS_SECRET_ACCESS_KEY={credentials['SecretAccessKey']}",
        "-e", f"AWS_SESSION_TOKEN={credentials['SessionToken']}",
        "-e", "AWS_DEFAULT_REGION=us-east-1",
        f"{ecr_url}:latest"
    ], check=True)
    
    print("Container running at http://localhost:8501")

if __name__ == "__main__":
    deploy_docker_locally()
