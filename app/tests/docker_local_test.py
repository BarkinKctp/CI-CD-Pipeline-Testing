import logging
import os
import subprocess
import tempfile

from parameters_validation import non_blank, non_empty, validate_parameters
from app.build_local_packages import InputOutputParameters, build_packages
from app.validation import run_command
from app.validation import ValidationError, format_env_error, validate_required_env

logger = logging.getLogger(__name__)


# pyright: reportInvalidTypeForm=false
@validate_parameters
def _validate_local_flow_inputs(
    gh_token: non_empty(non_blank(str)),
    target_repo: non_empty(non_blank(str)),
    target_branch: non_empty(non_blank(str)),
    docker_image: non_empty(non_blank(str)),
):
    return gh_token, target_repo, target_branch, docker_image


def push_test_results(target_repo: str, target_branch: str) -> None:
    """Push test results to target repository."""
    github_event = os.environ.get('GITHUB_EVENT_NAME', '')
    if github_event == 'pull_request':
        logger.info('Pull request event detected. Skipping push to target repo.')
        return

    github_run_id = os.environ.get('GITHUB_RUN_ID', 'unknown')
    github_run_number = os.environ.get('GITHUB_RUN_NUMBER', 'unknown')
    github_workflow = os.environ.get('GITHUB_WORKFLOW', 'unknown')
    github_repository = os.environ.get('GITHUB_REPOSITORY', 'unknown')
    github_ref = os.environ.get('GITHUB_REF', 'unknown')

    os.makedirs('results', exist_ok=True)
    result_file = f'results/test-flask-{github_run_id}.md'

    with open(result_file, 'w') as f:
        f.write(f'''# Test Flask Workflow Result

- Status: success
- Repository: {github_repository}
- Branch/Ref: {github_ref}
- Run ID: {github_run_id}
- Run Number: {github_run_number}
- Workflow: {github_workflow}
''')

    logger.info(f'Wrote test result to {result_file}')

    with tempfile.TemporaryDirectory() as workdir:
        target_path = os.path.join(workdir, 'target')
        run_command(['git', 'clone', f'https://github.com/{target_repo}.git', target_path],
                    shell=False, capture_output=True)

        os.makedirs(os.path.join(target_path, 'results'), exist_ok=True)

        target_result_file = os.path.join(target_path, result_file)
        os.makedirs(os.path.dirname(target_result_file), exist_ok=True)

        with open(target_result_file, 'w') as f:
            with open(result_file, 'r') as src:
                f.write(src.read())

        run_command(['git', '-C', target_path, 'config', 'user.name', 'github-actions[bot]'],
                    shell=False, capture_output=True)
        run_command(['git', '-C', target_path, 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'],
                    shell=False, capture_output=True)
        run_command(['git', '-C', target_path, 'checkout', target_branch],
                    shell=False, capture_output=True)
        run_command(['git', '-C', target_path, 'add', result_file],
                    shell=False, capture_output=True)

        diff = subprocess.run(['git', '-C', target_path, 'diff', '--cached', '--quiet'], capture_output=True)
        if diff.returncode == 0:
            logger.info('No result changes to push.')
            return

        run_command(['git', '-C', target_path, 'commit', '-m', f'Add test result for run {github_run_id}'],
                    shell=False, capture_output=True)
        run_command(['git', '-C', target_path, 'push', 'origin', target_branch],
                    shell=False, capture_output=True)
        logger.info(f'Pushed {result_file} to {target_repo}:{target_branch}')


def test_build_local_packages():
    """Run local Docker build/test flow and push test results."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        env_vars = validate_required_env(['GH_TOKEN', 'TARGET_REPO'])
        gh_token = env_vars['GH_TOKEN']
        target_repo = env_vars['TARGET_REPO']
        target_branch = (os.getenv('TARGET_BRANCH', 'main') or 'main').strip()
        docker_image = (os.getenv('DOCKER_IMAGE', 'flask-app-test') or 'flask-app-test').strip()
        gh_token, target_repo, target_branch, docker_image = _validate_local_flow_inputs(
            gh_token=gh_token,
            target_repo=target_repo,
            target_branch=target_branch,
            docker_image=docker_image,
        )
    except ValidationError as e:
        raise AssertionError(format_env_error(['GH_TOKEN', 'TARGET_REPO'], str(e))) from e

    io_parameters = InputOutputParameters.build(output_dir="artifacts")

    logger.info("Building and testing local image")
    build_packages(
        github_token=gh_token,
        target_repo=target_repo,
        docker_image=docker_image,
        io_parameters=io_parameters,
    )
    push_test_results(target_repo, target_branch)
