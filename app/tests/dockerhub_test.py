import logging
import os

from parameters_validation import non_blank, non_empty, validate_parameters
from app.build_dockerhub_packages import (
    InputOutputParameters,
    build_image,
    push_image,
    run_image_tests,
)
from app.validation import get_required_env, ValidationError, format_env_error

logger = logging.getLogger(__name__)

@validate_parameters
def _validate_dockerhub_flow_inputs(
    gh_token: non_empty(non_blank(str)),
    target_repo: non_empty(non_blank(str)),
    docker_image: non_empty(non_blank(str)),
    dockerfile_path: non_empty(non_blank(str)),
):
    return gh_token, target_repo, docker_image, dockerfile_path


def test_build_packages():
    """Run DockerHub image build/test/push flow."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    try:
        env_vars = get_required_env(['GH_TOKEN', 'TARGET_REPO', 'DOCKER_TEST_IMAGE'])
        gh_token = env_vars['GH_TOKEN']
        target_repo = env_vars['TARGET_REPO']
        docker_image = env_vars['DOCKER_TEST_IMAGE']
    except ValidationError as e:
        raise AssertionError(format_env_error(['GH_TOKEN', 'TARGET_REPO', 'DOCKER_TEST_IMAGE'], str(e))) from e

    sha_image_tag = os.getenv('SHA_IMAGE_TAG', '')
    dockerfile_path = (os.getenv('DOCKERFILE_PATH', 'docker/dockerhub-image/Dockerfile') or 'docker/dockerhub-image/Dockerfile').strip()
    gh_token, target_repo, docker_image, dockerfile_path = _validate_dockerhub_flow_inputs(
        gh_token=gh_token,
        target_repo=target_repo,
        docker_image=docker_image,
        dockerfile_path=dockerfile_path,
    )

    io_parameters = InputOutputParameters.build(output_dir='artifacts')

    logger.info("Building, testing, and pushing Docker image")
    build_image(dockerfile_path=dockerfile_path, docker_image=docker_image)
    run_image_tests(
        github_token=gh_token,
        target_repo=target_repo,
        docker_image=docker_image,
        io_parameters=io_parameters,
    )
    push_image(docker_image=docker_image, sha_image_tag=sha_image_tag)
