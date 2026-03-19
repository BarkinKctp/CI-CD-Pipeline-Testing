import os
from dataclasses import dataclass

from parameters_validation import non_blank, non_empty, validate_parameters
from app.validation import run_command


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
    run_command(['docker', 'build', '-f', dockerfile_path, '-t', docker_image, '.'],
               shell=False, capture_output=False)


@validate_parameters
def run_image_tests(
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
    run_command(['docker', 'push', docker_image],
               shell=False, capture_output=False)
    
    if sha_image_tag:
        run_command(['docker', 'tag', docker_image, sha_image_tag],
                   shell=False, capture_output=False)
        run_command(['docker', 'push', sha_image_tag],
                   shell=False, capture_output=False)