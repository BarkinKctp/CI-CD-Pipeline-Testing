import os
import subprocess
from typing import Dict, List


class ValidationError(Exception):
    pass


ENV_VARS_HELP = {
    'GH_TOKEN': 'Required secret from GitHub App',
    'TARGET_REPO': 'Should be set as workflow env var',
    'DOCKER_TEST_IMAGE': 'Should be set as workflow env var (e.g. youruser/ghapp-test:latest)',
    'DOCKER_IMAGE': 'Should be set as workflow env var (e.g. youruser/ghapp-test:latest)',
}


def format_env_error(missing_vars: list, base_error: str = '') -> str:
    lines = []
    if base_error:
        lines.append(f"Missing required environment variables: {base_error}")
    else:
        lines.append(f"Missing required environment variables: {', '.join(missing_vars)}")
    for var in missing_vars:
        help_text = ENV_VARS_HELP.get(var, 'Required')
        lines.append(f"  - {var}: {help_text}")
    return '\n'.join(lines)


def get_required_env(var_names: List[str], strip: bool = True) -> Dict[str, str]:
    missing = []
    result = {}
    
    for var_name in var_names:
        value = os.getenv(var_name, '')
        if strip:
            value = value.strip()
        
        if not value:
            missing.append(var_name)
        else:
            result[var_name] = value
    
    if missing:
        raise ValidationError(format_env_error(missing))
    
    return result



def validate_required_env(required_vars: list):
    return get_required_env(required_vars, strip=True)





def run_command(command, shell=False, capture_output=True, env=None):
    try:
        result = subprocess.run(
            command,
            shell=shell,
            text=True,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            check=True,
            env=env
        )
        return result
    except subprocess.CalledProcessError as e:
        cmd_str = command if isinstance(command, str) else " ".join(command)
        error_msg = f"Command failed with exit code {e.returncode}: {cmd_str}"
        if e.stderr:
            error_msg += f"\nStderr: {e.stderr}"
        if e.stdout:
            error_msg += f"\nStdout: {e.stdout}"
        raise RuntimeError(error_msg) from e


