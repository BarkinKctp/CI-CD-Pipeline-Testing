import logging
import os
from dataclasses import dataclass

from parameters_validation import non_blank, non_empty, validate_parameters
from app.validation import run_command, validate_required_env

logger = logging.getLogger(__name__)


@dataclass
class InputOutputParameters:
    output_dir: str = "artifacts"

    @staticmethod
    @validate_parameters
    def build(output_dir: non_empty(non_blank(str)) = "artifacts"):
        return InputOutputParameters(output_dir=output_dir)


@validate_parameters
def build_image(
    dockerfile_path: non_empty(non_blank(str)) = "docker/dockerhub-image/Dockerfile",
    docker_image: non_empty(non_blank(str)) = "brkndocker/ghapp-test:latest",
) -> None:
    """Build Docker image."""
    logger.info(f"Building image: {docker_image}")
    run_command(['docker', 'build', '-f', dockerfile_path, '-t', docker_image, '.'],
               shell=False, capture_output=False)


@validate_parameters
def test_image(
    github_token: non_empty(non_blank(str)),
    target_repo: non_empty(non_blank(str)),
    docker_image: non_empty(non_blank(str)),
    io_parameters: InputOutputParameters = None,
) -> None:
    """Test Docker image. Raises RuntimeError if tests fail."""
    if io_parameters is None:
        io_parameters = InputOutputParameters.build()
    
    os.environ["GH_TOKEN"] = github_token
    os.makedirs(io_parameters.output_dir, exist_ok=True)

    logger.info(f"Testing image: {docker_image}")
    run_command(['docker', 'run', '--rm', '-e', 'GH_TOKEN', 
                '-e', f'TARGET_REPO={target_repo}',
                '-e', 'GITHUB_ACTIONS=true',
                docker_image, 'pytest', '-q', 'app/tests/app_test.py'],
               shell=False, capture_output=False)


@validate_parameters
def push_image(
    docker_image: non_empty(non_blank(str)),
    sha_image_tag: str = "",
) -> None:
    """Push Docker image to registry."""
    logger.info(f"Pushing image: {docker_image}")
    run_command(['docker', 'push', docker_image],
               shell=False, capture_output=False)
    
    if sha_image_tag:
        logger.info(f"Tagging and pushing SHA image: {sha_image_tag}")
        run_command(['docker', 'tag', docker_image, sha_image_tag],
                   shell=False, capture_output=False)
        run_command(['docker', 'push', sha_image_tag],
                   shell=False, capture_output=False)





def run_build_test_push():
    """Build image, test it, and push only if tests pass."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    github_token = os.getenv('GH_TOKEN', '')
    target_repo = os.getenv('TARGET_REPO', '')
    docker_image = os.getenv('DOCKER_TEST_IMAGE', 'brkndocker/ghapp-test:latest')
    sha_image_tag = os.getenv('SHA_IMAGE_TAG', '')
    dockerfile_path = os.getenv('DOCKERFILE_PATH', 'docker/dockerhub-image/Dockerfile')
    
    validate_required_env(['GH_TOKEN', 'TARGET_REPO'])
    
    io_parameters = InputOutputParameters.build(output_dir="artifacts")
    
    # Build image
    build_image(dockerfile_path, docker_image)
    
    # Test image (raises RuntimeError if tests fail)
    test_image(github_token, target_repo, docker_image, io_parameters)
    
    # Push only if tests pass
    push_image(docker_image, sha_image_tag)
    logger.info("Build, test, and push completed successfully!")


if __name__ == '__main__':
    run_build_test_push()