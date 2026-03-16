import os

from app.build_local_packages import InputOutputParameters, build_packages
from app.validation import ValidationError, format_env_error


def test_build_local_packages():
    """Test GitHub App token authentication by cloning FROM the build host.
    
    This validates that:
    1. The GH_TOKEN is available in the GitHub Actions environment
    2. Git clone can be performed from the host using GH_TOKEN
    3. The Flask app tests run successfully with the cloned repository
    """
    try:
        gh_token = os.getenv('GH_TOKEN', '')
        target_repo = os.getenv('TARGET_REPO', '')
        
        if not gh_token:
            raise ValidationError('GH_TOKEN is required')
        if not target_repo:
            raise ValidationError('TARGET_REPO is required')
    except ValidationError as e:
        raise AssertionError(format_env_error(['GH_TOKEN', 'TARGET_REPO'], str(e))) from e

    io_parameters = InputOutputParameters.build(output_dir="artifacts")

    # This builds the local image and runs app_test.py inside the container
    build_packages(
        github_token=gh_token,
        target_repo=target_repo,
        docker_image="flask-app-test",
        io_parameters=io_parameters,
    )
