import boto3
import pytest
from datetime import datetime, timedelta

def test_codebuild_success():
    """Test that latest CodeBuild succeeded"""
    client = boto3.client('codebuild', region_name='us-east-1')
    
    builds = client.list_builds_for_project(
        projectName='osintube-build',
        sortOrder='DESCENDING'
    )
    
    latest_build = client.batch_get_builds(ids=[builds['ids'][0]])
    build = latest_build['builds'][0]
    
    assert build['buildStatus'] == 'SUCCEEDED', f"Build failed: {build['buildStatus']}"
    assert build['currentPhase'] == 'COMPLETED'

def test_ecr_image_exists():
    """Test that Docker image was pushed to ECR"""
    client = boto3.client('ecr', region_name='us-east-1')
    
    try:
        response = client.describe_images(
            repositoryName='osintube',
            imageIds=[{'imageTag': 'latest'}]
        )
        assert len(response['imageDetails']) > 0, "No latest image found in ECR"
        
        # Check image was pushed recently (within last hour)
        latest_image = response['imageDetails'][0]
        push_time = latest_image['imagePushedAt']
        now = datetime.now(push_time.tzinfo)
        
        assert (now - push_time) < timedelta(hours=1), "Image not recently pushed"
        
    except client.exceptions.ImageNotFoundException:
        pytest.fail("Latest image not found in ECR repository")

def test_ssm_parameters():
    """Test that required SSM parameters exist"""
    client = boto3.client('ssm', region_name='us-east-1')
    
    required_params = [
        '/osintube/ecr_repository_uri',
        '/osintube/container_name',
        '/osintube/container_port'
    ]
    
    for param in required_params:
        response = client.get_parameter(Name=param)
        assert response['Parameter']['Value'], f"Parameter {param} is empty"
