import os
import subprocess
import tempfile
import pytest

from app.validation import validate_required_env, ValidationError


def test_gh_token_can_clone_target_repo():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        pytest.skip('GH token clone test only runs in GitHub Actions.')

    try:
        env_vars = validate_required_env(['GH_TOKEN', 'TARGET_REPO'])
        target_repo = env_vars['TARGET_REPO']
        gh_token = env_vars['GH_TOKEN']
    except ValidationError as e:
        pytest.fail(f'Validation failed: {str(e)}')

    repo_url = f'https://github.com/{target_repo}.git'

    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = os.path.join(temp_dir, 'repo-under-test')
        env = os.environ.copy()
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, clone_dir],
            env=env,
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, f'git clone failed for {target_repo}. Exit code: {result.returncode}. stderr: {result.stderr.strip()}'

        verify = subprocess.run(
            ['git', '-C', clone_dir, 'rev-parse', '--is-inside-work-tree'],
            capture_output=True, text=True, check=False,
        )
        assert verify.returncode == 0, f'Clone directory is not a valid git work tree. stderr: {verify.stderr.strip()}'
        assert verify.stdout.strip() == 'true', 'git clone succeeded but cloned directory is not recognized as a git work tree.'
