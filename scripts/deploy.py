#!/usr/bin/env python3
import subprocess
import time
import sys

def trigger_build():
    """Trigger CodeBuild project"""
    print("🚀 Triggering CodeBuild...")
    result = subprocess.run([
        "aws", "codebuild", "start-build",
        "--project-name", "osintube-build",
        "--region", "us-east-1"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ CodeBuild failed: {result.stderr}")
        sys.exit(1)
    
    print("✅ CodeBuild triggered successfully")
    return True

def wait_for_build():
    """Wait for build to complete"""
    print("⏳ Waiting for build to complete...")
    time.sleep(60)  # Wait 1 minute for build to finish
    print("✅ Build should be complete")

def rollout_deployment():
    """Rollout EKS deployment"""
    print("🔄 Rolling out latest image...")
    
    # Restart deployment
    subprocess.run([
        "kubectl", "rollout", "restart", "deployment/osintube-app"
    ], check=True)
    
    # Wait for rollout
    print("⏳ Waiting for rollout to complete...")
    subprocess.run([
        "kubectl", "rollout", "status", "deployment/osintube-app", "--timeout=300s"
    ], check=True)
    
    print("✅ Rollout completed - latest image deployed!")

def main():
    """Combined trigger and rollout"""
    try:
        trigger_build()
        wait_for_build()
        rollout_deployment()
        print("🎉 Deployment complete!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
