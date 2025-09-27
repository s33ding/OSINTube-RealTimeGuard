#!/bin/bash

# Script to manually trigger CodeBuild for OSINTube project

echo "Triggering CodeBuild for OSINTube project..."

BUILD_ID=$(aws codebuild start-build \
    --project-name osintube-build \
    --region us-east-1 \
    --query 'build.id' \
    --output text)

if [ $? -eq 0 ]; then
    echo "Build triggered successfully!"
    echo "Build ID: $BUILD_ID"
    echo "You can monitor the build at:"
    echo "https://console.aws.amazon.com/codesuite/codebuild/projects/osintube-build/build/$BUILD_ID"
else
    echo "Failed to trigger build"
    exit 1
fi
