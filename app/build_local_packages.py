import logging
import os
import subprocess
import tempfile
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


def push_test_results(target_repo: str, target_branch: str) -> None:
    """Push test results to target repository."""
    github_event = os.getenv('GITHUB_EVENT_NAME', '')
    if github_event == 'pull_request':
        logger.info('Pull request event detected. Skipping push to target repo.')
        return

    github_run_id = os.getenv('GITHUB_RUN_ID', 'unknown')
    github_run_number = os.getenv('GITHUB_RUN_NUMBER', 'unknown')
    github_workflow = os.getenv('GITHUB_WORKFLOW', 'unknown')
    github_repository = os.getenv('GITHUB_REPOSITORY', 'unknown')
    github_ref = os.getenv('GITHUB_REF', 'unknown')
    
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
    
    github_token = os.getenv('GH_TOKEN', '')
    with tempfile.TemporaryDirectory() as workdir:
        target_path = os.path.join(workdir, 'target')
        run_command(['git', 'clone', f'https://{github_token}@github.com/{target_repo}.git', target_path], 
                   shell=False, capture_output=True)
        
        os.makedirs(os.path.join(target_path, 'results'), exist_ok=True)
        
        target_result_file = os.path.join(target_path, result_file)
        os.makedirs(os.path.dirname(target_result_file), exist_ok=True)
        
        with open(target_result_file, 'w') as f:
            with open(result_file, 'r') as src:
                f.write(src.read())
        
        os.chdir(target_path)
        run_command(['git', 'config', 'user.name', 'github-actions[bot]'], 
                   shell=False, capture_output=True)
        run_command(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'], 
                   shell=False, capture_output=True)
        run_command(['git', 'checkout', target_branch], 
                   shell=False, capture_output=True)
        run_command(['git', 'add', result_file], 
                   shell=False, capture_output=True)
        
        diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
        if diff.returncode == 0:
            logger.info('No result changes to push.')
            return
        
        run_command(['git', 'commit', '-m', f'Add test result for run {github_run_id}'], 
                   shell=False, capture_output=True)
        run_command(['git', 'push', 'origin', target_branch], 
                   shell=False, capture_output=True)
        logger.info(f'Pushed {result_file} to {target_repo}:{target_branch}')


def run_build_packages():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    github_token = os.getenv('GH_TOKEN', '')
    target_repo = os.getenv('TARGET_REPO', '')
    target_branch = os.getenv('TARGET_BRANCH', 'main')
    docker_image = os.getenv('DOCKER_IMAGE', 'flask-app-test')
    
    validate_required_env(['GH_TOKEN', 'TARGET_REPO'])  
    
    io_parameters = InputOutputParameters.build(output_dir="artifacts")
    build_packages(github_token, target_repo, docker_image, io_parameters)
    push_test_results(target_repo, target_branch)


if __name__ == '__main__':
    run_build_packages()
