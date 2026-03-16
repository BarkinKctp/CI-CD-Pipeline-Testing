import subprocess

from app.build_dockerhub_packages import InputOutputParameters, build_packages
from app.validation import get_required_env, ValidationError, format_env_error


def test_build_packages():
    """Test GitHub App token authentication by cloning INSIDE the DockerHub container.
    
    This validates that:
    1. The GH_TOKEN is passed into the container successfully
    2. The entrypoint.sh script can use GH_TOKEN to clone the target repo
    3. Git clone with retry logic works inside the container environment
    """
    try:
        env_vars = get_required_env(['GH_TOKEN', 'TARGET_REPO', 'DOCKER_TEST_IMAGE'])
        gh_token = env_vars['GH_TOKEN']
        target_repo = env_vars['TARGET_REPO']
        docker_image = env_vars['DOCKER_TEST_IMAGE']
    except ValidationError as e:
        raise AssertionError(format_env_error(['GH_TOKEN', 'TARGET_REPO', 'DOCKER_TEST_IMAGE'], str(e))) from e

    pull = subprocess.run(["docker", "pull", docker_image], capture_output=True, text=True)
    assert pull.returncode == 0, (
        f"Could not pull Docker image '{docker_image}'.\n"
        f"  - Run the 'Publish GH App Test Image' workflow first to push the image to DockerHub.\n"
        f"  - Ensure DOCKERHUB_USERNAME and DOCKERHUB_TOKEN secrets are set.\n"
        f"  - Verify DOCKER_TEST_IMAGE in the workflow matches the published image name.\n"
        f"Docker error: {pull.stderr.strip()}"
    )

    io_parameters = InputOutputParameters.build(output_dir="artifacts")

    # This runs the image with entrypoint.sh, which performs git clone inside container
    build_packages(
        github_token=gh_token,
        target_repo=target_repo,
        docker_image=docker_image,
        io_parameters=io_parameters,
    )
