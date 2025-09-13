# OSINTube-RealTimeGuard Deployment Guide

## Project Structure

```
├── iac/                    # Terraform Infrastructure as Code
├── docker-image/           # Docker build configuration
├── eks/                    # Kubernetes manifests
├── app/                    # Application code
└── buildspec.yml          # AWS CodeBuild specification
```

## Deployment Steps

### 1. Infrastructure Setup (Terraform)
```bash
cd iac
terraform init
terraform plan
terraform apply
```

### 2. Build Docker Image
```bash
cd docker-image
./build.sh
```

### 3. Deploy to EKS
```bash
cd eks
kubectl apply -f serviceaccount.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### 4. CI/CD with CodeBuild
The `buildspec.yml` file handles automated builds and deployments through AWS CodeBuild.

## Configuration

- **Secrets**: Stored in AWS Secrets Manager
- **Parameters**: Stored in AWS Systems Manager Parameter Store
- **Storage**: Amazon S3 for data persistence
- **Container Registry**: Amazon ECR
- **Orchestration**: Amazon EKS
