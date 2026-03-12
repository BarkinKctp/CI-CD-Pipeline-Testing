import subprocess

from app.gh_token_platform import build_gh_token_platform
from parameters_validation import non_empty, non_blank


def build_packages(gh_token, platform):
    non_empty(non_blank(str))(gh_token, 'gh_token')

    context = build_gh_token_platform()
    image_name = context['image_name']
    target_repo = context['target_repo']
    github_actions = context['github_actions']

    commands = [
        ['docker', 'build', '-f', 'docker/ghapp-image/Dockerfile', '-t', image_name, '.'],
        [
            'docker',
            'run',
            '--rm',
            '-e',
            f'GH_TOKEN={gh_token}',
            '-e',
            f'TARGET_REPO={target_repo}',
            '-e',
            f'GITHUB_ACTIONS={github_actions}',
            '-e',
            f'PLATFORM={platform}',
            image_name,
            'python',
            '-m',
            'unittest',
            'app/publish_test.py',
        ],
    ]
    return commands


def run_build_packages():
    context = build_gh_token_platform()
    gh_token = context['token']
    platform = context['platform']

    non_empty(non_blank(str))(gh_token, 'gh_token')

    for command in build_packages(gh_token, platform):
        subprocess.run(command, check=True)


if __name__ == '__main__':
    run_build_packages()