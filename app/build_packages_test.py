import os
import unittest
from unittest.mock import patch

from app.build_packages import build_packages


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
            ],
        )


if __name__ == '__main__':
    unittest.main()