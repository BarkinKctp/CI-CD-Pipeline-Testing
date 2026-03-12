import os
import subprocess
from dataclasses import dataclass


@dataclass
class InputOutputParameters:
    output_dir: str = "artifacts"


def run_with_output(command: str):
    return subprocess.run(
        command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def build_package(
    github_token: str,
    target_repo: str,
    docker_image: str,
    io_parameters: InputOutputParameters,
) -> None:
    if not github_token or not github_token.strip():
        raise ValueError("github_token must not be empty")

    if not target_repo or not target_repo.strip():
        raise ValueError("target_repo must not be empty")

    os.environ["GITHUB_TOKEN"] = github_token

    os.makedirs(io_parameters.output_dir, exist_ok=True)

    docker_command = (
        f'docker run --rm '
        f'-e GITHUB_TOKEN '
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


def build_packages(
    github_token: str,
    target_repo: str,
    docker_image: str,
    io_parameters: InputOutputParameters,
) -> None:
    build_package(
        github_token=github_token,
        target_repo=target_repo,
        docker_image=docker_image,
        io_parameters=io_parameters,
    )