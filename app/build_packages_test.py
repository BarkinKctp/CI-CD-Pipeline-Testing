import os
import unittest
from unittest.mock import patch

from parameters_validation import non_blank, non_empty

from app.build_packages import build_packages
from app.gh_token_platform import build_gh_token_platform


EXAMPLE_TOKEN = 'example-token'
TARGET_REPO = 'BarkinKctp/ghapp-oidc-deploy-test'
IMAGE_NAME = 'flask-app-test'
PLATFORM = 'debian'


class TestBuildPackages(unittest.TestCase):
    def test_build_packages_uses_gh_token_platform(self):
        with patch.dict(
            os.environ,
            {
                'TARGET_REPO': TARGET_REPO,
                'IMAGE_NAME': IMAGE_NAME,
            },
            clear=False,
        ):
            commands = build_packages(EXAMPLE_TOKEN, PLATFORM)

        self.assertEqual(commands[0], ['docker', 'build', '-t', IMAGE_NAME, '.'])
        self.assertEqual(
            commands[1],
            [
                'docker',
                'run',
                '--rm',
                '-e',
                f'GH_TOKEN={EXAMPLE_TOKEN}',
                '-e',
                f'TARGET_REPO={TARGET_REPO}',
                '-e',
                'GITHUB_ACTIONS=true',
                '-e',
                f'PLATFORM={PLATFORM}',
                IMAGE_NAME,
                'python',
                '-m',
                'unittest',
                'app/publish_test.py',
            ],
        )

    def test_build_packages_raises_on_empty_gh_token(self):
        with self.assertRaises(Exception):
            non_empty(str)('', 'gh_token')

    def test_build_packages_raises_on_blank_gh_token(self):
        with self.assertRaises(Exception):
            non_blank(str)('   ', 'gh_token')

    def test_gh_token_clone_url_format(self):
        with patch.dict(
            os.environ,
            {
                'GH_TOKEN': EXAMPLE_TOKEN,
                'TARGET_REPO': TARGET_REPO,
            },
            clear=False,
        ):
            platform = build_gh_token_platform()

        self.assertEqual(
            platform['clone_url'],
            f'https://x-access-token:{EXAMPLE_TOKEN}@github.com/{TARGET_REPO}.git',
        )

if __name__ == '__main__':
    unittest.main()