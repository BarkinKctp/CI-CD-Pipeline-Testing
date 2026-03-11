import unittest
import json
import os
import subprocess
import tempfile
from urllib import error, request

from app.main import app


class TestPublish(unittest.TestCase):
	def setUp(self):
		self.client = app.test_client()

	def test_home_page_loads(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertIn('html', response.get_data(as_text=True).lower())

	def test_reverse_api_for_numbers(self):
		response = self.client.get('/api/reverse/12345')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.get_data(as_text=True), '54321')

	def test_gh_token_can_clone_target_repo(self):
		if os.environ.get('GITHUB_ACTIONS') != 'true':
			self.skipTest('GH token clone test only runs in GitHub Actions.')

		token = os.environ.get('GH_TOKEN')
		target_repo = os.environ.get('TARGET_REPO')

		self.assertTrue(token, 'GH_TOKEN is missing in workflow test environment.')
		self.assertTrue(target_repo, 'TARGET_REPO is missing in workflow test environment.')

		repo_url = f'https://x-access-token:{token}@github.com/{target_repo}.git'

		with tempfile.TemporaryDirectory() as temp_dir:
			clone_dir = os.path.join(temp_dir, 'repo-under-test')
			result = subprocess.run(
				['git', 'clone', '--depth', '1', repo_url, clone_dir],
				capture_output=True,
				text=True,
				check=False,
			)

		self.assertEqual(
			result.returncode,
			0,
			f'git clone failed for {target_repo}. Exit code: {result.returncode}',
		)
		self.assertTrue(
			os.path.isdir(os.path.join(clone_dir, '.git')),
			'git clone reported success but no .git directory was found.',
		)


if __name__ == '__main__':
	unittest.main()
