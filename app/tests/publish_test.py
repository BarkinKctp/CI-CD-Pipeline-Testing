import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from app.main import app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_return_backwards_string(self):
        response = self.client.get('/api/reverse/Hello,%20World!')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '!dlroW ,olleH')

    def test_get_env(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get('/get-mode')
            self.assertEqual(response.status_code, 200)
            self.assertIn('No mode set', response.get_data(as_text=True))


class TestPublish(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.get_data(as_text=True).lower())

    def test_gh_token_can_clone_target_repo(self):
        if os.environ.get('GITHUB_ACTIONS') != 'true':
            self.skipTest('GH token clone test only runs in GitHub Actions.')

        token = os.environ.get('GH_TOKEN', '')
        target_repo = os.environ.get('TARGET_REPO', '')
        repo_url = f'https://x-access-token:{token}@github.com/{target_repo}.git' if token and target_repo else ''

        self.assertTrue(token, 'GH_TOKEN is missing in workflow test environment.')
        self.assertTrue(target_repo, 'TARGET_REPO is missing in workflow test environment.')
        self.assertTrue(repo_url, 'Authenticated clone URL could not be built from GH_TOKEN and TARGET_REPO.')

        with tempfile.TemporaryDirectory() as temp_dir:
            clone_dir = os.path.join(temp_dir, 'repo-under-test')
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, clone_dir],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0,
                f'git clone failed for {target_repo}. Exit code: {result.returncode}. stderr: {result.stderr.strip()}')

            verify = subprocess.run(
                ['git', '-C', clone_dir, 'rev-parse', '--is-inside-work-tree'],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(verify.returncode, 0,
                f'Clone directory is not a valid git work tree. stderr: {verify.stderr.strip()}')
            self.assertEqual(verify.stdout.strip(), 'true',
                'git clone succeeded but cloned directory is not recognized as a git work tree.')


if __name__ == '__main__':
    unittest.main()
