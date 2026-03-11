import unittest
import json
import os
import subprocess
import tempfile
from urllib import error, request

from app.main import app
from app.gh_token_platform import build_gh_token_platform


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

		platform = build_gh_token_platform()
		token = platform['token']
		target_repo = platform['target_repo']
		repo_url = platform['clone_url']

		self.assertTrue(token, 'GH_TOKEN is missing in workflow test environment.')
		self.assertTrue(target_repo, 'TARGET_REPO is missing in workflow test environment.')
		self.assertTrue(repo_url, 'Authenticated clone URL could not be built from GH_TOKEN platform context.')

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
				f'git clone failed for {target_repo}. Exit code: {result.returncode}. stderr: {result.stderr.strip()}',
			)

			verify = subprocess.run(
				['git', '-C', clone_dir, 'rev-parse', '--is-inside-work-tree'],
				capture_output=True,
				text=True,
				check=False,
			)
			self.assertEqual(
				verify.returncode,
				0,
				f'Clone directory is not a valid git work tree. stderr: {verify.stderr.strip()}',
			)
			self.assertEqual(
				verify.stdout.strip(),
				'true',
				'git clone succeeded but cloned directory is not recognized as a git work tree.',
			)


if __name__ == '__main__':
	unittest.main()
