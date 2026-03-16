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
    image_name: non_empty(non_blank(str)) = "flask-app-test",
    io_parameters: InputOutputParameters = None,
) -> None:
    if io_parameters is None:
        io_parameters = InputOutputParameters.build()
    
    os.environ["GH_TOKEN"] = github_token
    os.makedirs(io_parameters.output_dir, exist_ok=True)

    commands = [
        ['docker', 'build', '-f', 'docker/local-image/Dockerfile', '-t', image_name, '.'],
        ['docker', 'run', '--rm', '-e', f'GH_TOKEN={github_token}', 
         '-e', f'TARGET_REPO={target_repo}', '-e', 'GITHUB_ACTIONS=true', 
         image_name, 'pytest', '-q', 'app/tests/app_test.py'],
    ]
    
    for command in commands:
        run_command(command, shell=False, capture_output=False)


def run_build_packages():
    github_token = os.getenv('GH_TOKEN', '')
    target_repo = os.getenv('TARGET_REPO', '')
    image_name = os.getenv('IMAGE_NAME', 'flask-app-test')
    
    non_empty(non_blank(str))(github_token, 'GH_TOKEN')
    non_empty(non_blank(str))(target_repo, 'TARGET_REPO')
    
    io_parameters = InputOutputParameters.build(output_dir="artifacts")
    build_packages(github_token, target_repo, image_name, io_parameters)


if __name__ == '__main__':
    run_build_packages()
