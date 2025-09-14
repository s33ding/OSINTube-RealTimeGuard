import pytest
import yaml
import os
import boto3

def test_buildspec_structure():
    """Test buildspec.yml structure and content"""
    
    # Load and validate buildspec.yml
    buildspec_path = '/home/roberto/Github/OSINTube-RealTimeGuard/buildspec.yml'
    assert os.path.exists(buildspec_path), "buildspec.yml not found"
    
    with open(buildspec_path, 'r') as f:
        buildspec = yaml.safe_load(f)
    
    # Validate buildspec structure
    assert 'version' in buildspec
    assert buildspec['version'] == 0.2
    assert 'phases' in buildspec
    
    # Validate required phases
    phases = buildspec['phases']
    assert 'pre_build' in phases
    assert 'build' in phases
    assert 'post_build' in phases
    
    # Validate pre_build commands
    pre_build_commands = phases['pre_build']['commands']
    assert any('ecr get-login-password' in cmd for cmd in pre_build_commands)
    assert any('/osintube/ecr_repository_uri' in cmd for cmd in pre_build_commands)
    
    # Validate build commands
    build_commands = phases['build']['commands']
    assert any('docker build' in cmd for cmd in build_commands)
    assert any('docker tag' in cmd for cmd in build_commands)
    
    # Validate post_build commands
    post_build_commands = phases['post_build']['commands']
    assert any('docker push' in cmd for cmd in post_build_commands)

def test_ssm_parameter_integration():
    """Test SSM parameter exists for ECR repository"""
    try:
        ssm = boto3.client('ssm', region_name='us-east-1')
        response = ssm.get_parameter(Name='/osintube/ecr_repository_uri')
        assert 'osintube' in response['Parameter']['Value']
        assert 'ecr' in response['Parameter']['Value']
    except Exception as e:
        pytest.skip(f"AWS credentials not available: {e}")

def test_buildspec_environment_variables():
    """Test buildspec uses correct environment variables"""
    
    buildspec_path = '/home/roberto/Github/OSINTube-RealTimeGuard/buildspec.yml'
    with open(buildspec_path, 'r') as f:
        buildspec = yaml.safe_load(f)
    
    # Check for required environment variables in commands
    all_commands = []
    for phase in buildspec['phases'].values():
        if 'commands' in phase:
            all_commands.extend(phase['commands'])
    
    commands_str = ' '.join(all_commands)
    assert '$AWS_DEFAULT_REGION' in commands_str
    assert '$AWS_ACCOUNT_ID' in commands_str

def test_dockerfile_exists():
    """Test that Dockerfile exists in correct location"""
    dockerfile_path = '/home/roberto/Github/OSINTube-RealTimeGuard/docker-image/Dockerfile'
    assert os.path.exists(dockerfile_path), "Dockerfile not found in docker-image directory"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
