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
    docker_image: non_empty(non_blank(str)),
    io_parameters: InputOutputParameters,
) -> None:
    os.environ["GH_TOKEN"] = github_token
    os.makedirs(io_parameters.output_dir, exist_ok=True)

    docker_command = (
        f'docker run --rm '
        f'-e GH_TOKEN '
        f'-e TARGET_REPO="{target_repo}" '
        f'-v "{os.path.abspath(io_parameters.output_dir)}:/artifacts" '
        f'{docker_image}'
    )

    print(f"Executing docker command: {docker_command}")
    result = run_command(docker_command, shell=True, capture_output=True)

    if result.stdout:
        print(result.stdout)