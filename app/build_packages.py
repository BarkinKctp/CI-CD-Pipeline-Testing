import os
import subprocess

from parameters_validation import non_empty, non_blank


def get_context():
    token = os.environ.get('GH_TOKEN', '')
    target_repo = os.environ.get('TARGET_REPO', '')
    platform = os.environ.get('PLATFORM', 'debian')
    image_name = os.environ.get('IMAGE_NAME', 'flask-app-test')
    clone_url = f'https://x-access-token:{token}@github.com/{target_repo}.git' if token and target_repo else ''
    return {
        'token': token,
        'target_repo': target_repo,
        'platform': platform,
        'image_name': image_name,
        'clone_url': clone_url,
    }


def build_packages(gh_token, platform):
    non_empty(non_blank(str))(gh_token, 'gh_token')

    context = get_context()
    image_name = context['image_name']
    target_repo = context['target_repo']

    commands = [
        ['docker', 'build', '-f', 'docker/local-image/Dockerfile', '-t', image_name, '.'],
        ['docker', 'run', '--rm', '-e', f'GH_TOKEN={gh_token}', '-e', f'TARGET_REPO={target_repo}', '-e', 'GITHUB_ACTIONS=true', 
         '-e', f'PLATFORM={platform}', image_name, 'python', '-m', 'unittest', 'app.tests.publish_test'],
    ]
    return commands


def run_build_packages():
    context = get_context()
    gh_token = context['token']
    platform = context['platform']

    non_empty(non_blank(str))(gh_token, 'gh_token')

    for command in build_packages(gh_token, platform):
        subprocess.run(command, check=True)


if __name__ == '__main__':
    run_build_packages()