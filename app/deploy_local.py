#!/usr/bin/env python3
import subprocess

def deploy_docker_locally():
    """Deploy Docker container locally using ECR image"""
    # Get ECR repository URL
    result = subprocess.run([
        "aws", "ssm", "get-parameter", 
        "--name", "/osintube/ecr_repository_uri",
        "--query", "Parameter.Value",
        "--output", "text",
        "--region", "us-east-1"
    ], capture_output=True, text=True, check=True)
    
    ecr_url = result.stdout.strip()
    
    # Login to ECR
    login_cmd = subprocess.run([
        "aws", "ecr", "get-login-password", 
        "--region", "us-east-1"
    ], capture_output=True, text=True, check=True)
    
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
        "--rm",
        f"{ecr_url}:latest"
    ], check=True)
    
    print("Container running at http://localhost:8501")

if __name__ == "__main__":
    deploy_docker_locally()
