import os

from app.ghapp_docker import InputOutputParameters, build_packages


def test_build_packages():
    gh_token = os.getenv("GH_TOKEN")
    target_repo = os.getenv("TARGET_REPO")
    docker_image = os.getenv("DOCKER_TEST_IMAGE")

    if not gh_token:
        raise ValueError("GH_TOKEN is missing")

    if not target_repo:
        raise ValueError("TARGET_REPO is missing")

    if not docker_image:
        raise ValueError("DOCKER_TEST_IMAGE is missing")

    io_parameters = InputOutputParameters(output_dir="artifacts")

    build_packages(
        github_token=gh_token,
        target_repo=target_repo,
        docker_image=docker_image,
        io_parameters=io_parameters,
    )
