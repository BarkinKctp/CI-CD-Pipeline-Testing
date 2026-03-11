import os
import unittest
from unittest.mock import patch

from app.build_packages import build_packages
from app.gh_token_platform import build_gh_token_platform


class TestBuildPackages(unittest.TestCase):
    def test_build_packages_uses_gh_token_platform(self):
        with patch.dict(
            os.environ,
            {
                'TARGET_REPO': 'BarkinKctp/ghapp-oidc-deploy-test',
                'IMAGE_NAME': 'flask-app-test',
            },
            clear=False,
        ):
            commands = build_packages('example-token', 'debian')

        self.assertEqual(commands[0], ['docker', 'build', '-t', 'flask-app-test', '.'])
        self.assertEqual(
            commands[1],
            [
                'docker',
                'run',
                '--rm',
                '-e',
                'GH_TOKEN=example-token',
                '-e',
                'TARGET_REPO=BarkinKctp/ghapp-oidc-deploy-test',
                '-e',
                'GITHUB_ACTIONS=true',
                '-e',
                'PLATFORM=debian',
                'flask-app-test',
                'python',
                '-m',
                'unittest',
                'app/publish_test.py',
            ],
        )

    def test_gh_token_clone_url_format(self):
        with patch.dict(
            os.environ,
            {
                'GH_TOKEN': 'example-token',
                'TARGET_REPO': 'BarkinKctp/ghapp-oidc-deploy-test',
            },
            clear=False,
        ):
            platform = build_gh_token_platform()

        self.assertEqual(
            platform['clone_url'],
            'https://x-access-token:example-token@github.com/BarkinKctp/ghapp-oidc-deploy-test.git',
        )

if __name__ == '__main__':
    unittest.main()