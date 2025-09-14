#!/bin/bash

# EKS rollout script to pull latest images
set -e

echo "🔄 Rolling out latest image for OSINTube deployment..."

# Restart deployment to pull latest image
kubectl rollout restart deployment/osintube-app

# Wait for rollout to complete
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/osintube-app --timeout=300s

echo "✅ Rollout completed - latest image deployed!"
