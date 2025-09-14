#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime
import os

def monitor_codebuild():
    """Monitor latest CodeBuild process and save history"""
    history_file = "build_history.json"
    
    # Load existing history
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    # Get latest build
    result = subprocess.run([
        "aws", "codebuild", "list-builds-for-project",
        "--project-name", "osintube-build",
        "--region", "us-east-1"
    ], capture_output=True, text=True, check=True)
    
    builds = json.loads(result.stdout)
    if not builds['ids']:
        print("No builds found")
        return
    
    build_id = builds['ids'][0]
    print(f"Monitoring build: {build_id}")
    
    # Monitor build status
    while True:
        result = subprocess.run([
            "aws", "codebuild", "batch-get-builds",
            "--ids", build_id,
            "--region", "us-east-1"
        ], capture_output=True, text=True, check=True)
        
        build_data = json.loads(result.stdout)
        build = build_data['builds'][0]
        status = build['buildStatus']
        
        if status in ['SUCCEEDED', 'FAILED', 'STOPPED']:
            start_time = datetime.fromisoformat(build['startTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(build['endTime'].replace('Z', '+00:00'))
            duration = (end_time - start_time).total_seconds()
            
            # Save to history
            history.append({
                "build_id": build_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": status
            })
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            print(f"Build {status.lower()}: {duration:.1f}s")
            break
        
        print(f"Status: {status}")
        time.sleep(10)

if __name__ == "__main__":
    monitor_codebuild()
