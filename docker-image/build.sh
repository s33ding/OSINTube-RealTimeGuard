#!/bin/bash
# Get ECR repository URL from Parameter Store
ECR_URL=$(aws ssm get-parameter --name "/osintube/ecr_repository_url" --query 'Parameter.Value' --output text --region us-east-1)
docker build -t $ECR_URL:latest .
echo "Built image: $ECR_URL:latest"
