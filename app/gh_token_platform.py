import os


def build_gh_token_platform():
    token = os.environ.get('GH_TOKEN', '')
    target_repo = os.environ.get('TARGET_REPO', '')
    platform_name = os.environ.get('PLATFORM', 'debian')
    image_name = os.environ.get('IMAGE_NAME', 'flask-app-test')
    clone_url = ''

    if token and target_repo:
        clone_url = f'https://x-access-token:{token}@github.com/{target_repo}.git'

    return {
        'token': token,
        'target_repo': target_repo,
        'platform': platform_name,
        'image_name': image_name,
        'github_actions': 'true',
        'clone_url': clone_url,
    }
