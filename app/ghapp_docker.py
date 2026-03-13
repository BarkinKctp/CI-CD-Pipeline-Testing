import os
import subprocess
from dataclasses import dataclass

from parameters_validation import non_blank, non_empty, validate_parameters


@dataclass
class InputOutputParameters:
    output_dir: str = "artifacts"

    @staticmethod
    @validate_parameters
    def build(output_dir: non_empty(non_blank(str)) = "artifacts"):
        return InputOutputParameters(output_dir=output_dir)


def run_with_output(command: str):
    return subprocess.run(
        command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@validate_parameters
def build_package(
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
    result = run_with_output(docker_command)

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        raise ValueError(result.stderr or result.stdout or "docker run failed")


@validate_parameters
def build_packages(
    github_token: non_empty(non_blank(str)),
    target_repo: non_empty(non_blank(str)),
    docker_image: non_empty(non_blank(str)),
    io_parameters: InputOutputParameters,
) -> None:
    build_package(
        github_token=github_token,
        target_repo=target_repo,
        docker_image=docker_image,
        io_parameters=io_parameters,
    )