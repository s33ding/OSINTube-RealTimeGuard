#!/usr/bin/env python3
import subprocess

def trigger_codebuild():
    """Trigger CodeBuild project"""
    subprocess.run([
        "aws", "codebuild", "start-build",
        "--project-name", "osintube-build",
        "--region", "us-east-1"
    ], check=True)
    print("CodeBuild triggered successfully")

if __name__ == "__main__":
    trigger_codebuild()
