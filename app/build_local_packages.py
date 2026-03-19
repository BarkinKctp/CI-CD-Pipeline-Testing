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
def build_packages(
    github_token: non_empty(non_blank(str)),
    target_repo: non_empty(non_blank(str)),
    docker_image: non_empty(non_blank(str)) = "flask-app-test",
    io_parameters: InputOutputParameters = None,
) -> None:
    if io_parameters is None:
        io_parameters = InputOutputParameters.build()
    
    os.environ["GH_TOKEN"] = github_token
    os.makedirs(io_parameters.output_dir, exist_ok=True)

    commands = [
        ['docker', 'build', '-f', 'docker/local-image/Dockerfile', '-t', docker_image, '.'],
        ['docker', 'run', '--rm', '-e', 'GH_TOKEN',
         '-e', f'TARGET_REPO={target_repo}', '-e', 'GITHUB_ACTIONS=true', 
         docker_image, 'pytest', '-q', 'app/tests/app_test.py'],
    ]
    
    for command in commands:
        run_command(command, shell=False, capture_output=False)
