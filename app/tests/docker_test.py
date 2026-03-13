import os
import subprocess

from app.ghapp_docker import InputOutputParameters, build_packages


def test_build_packages():
    gh_token = os.getenv("GH_TOKEN")
    target_repo = os.getenv("TARGET_REPO")
    docker_image = os.getenv("DOCKER_TEST_IMAGE")

    assert gh_token, "GH_TOKEN is not set. Ensure GH_APPLICATION_ID and GH_APP_KEY secrets are configured for the GitHub App."
    assert target_repo, "TARGET_REPO is not set. It should be set as a job-level env var in the workflow."
    assert docker_image, "DOCKER_TEST_IMAGE is not set. It should be set as a job-level env var in the workflow (e.g. youruser/ghapp-test:latest)."

    pull = subprocess.run(["docker", "pull", docker_image], capture_output=True, text=True)
    assert pull.returncode == 0, (
        f"Could not pull Docker image '{docker_image}'.\n"
        f"  - Run the 'Publish GH App Test Image' workflow first to push the image to DockerHub.\n"
        f"  - Ensure DOCKERHUB_USERNAME and DOCKERHUB_TOKEN secrets are set.\n"
        f"  - Verify DOCKER_TEST_IMAGE in the workflow matches the published image name.\n"
        f"Docker error: {pull.stderr.strip()}"
    )

    io_parameters = InputOutputParameters.build(output_dir="artifacts")

    build_packages(
        github_token=gh_token,
        target_repo=target_repo,
        docker_image=docker_image,
        io_parameters=io_parameters,
    )