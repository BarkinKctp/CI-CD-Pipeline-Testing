import unittest
import json
import os
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

	def test_gh_token_can_access_target_repo(self):
		if os.environ.get('GITHUB_ACTIONS') != 'true':
			self.skipTest('GH token integration test only runs in GitHub Actions.')

		token = os.environ.get('GH_TOKEN')
		target_repo = os.environ.get('TARGET_REPO')

		self.assertTrue(token, 'GH_TOKEN is missing in workflow test environment.')
		self.assertTrue(target_repo, 'TARGET_REPO is missing in workflow test environment.')

		api_url = f'https://api.github.com/repos/{target_repo}'
		headers = {
			'Authorization': f'Bearer {token}',
			'Accept': 'application/vnd.github+json',
			'X-GitHub-Api-Version': '2022-11-28',
			'User-Agent': 'gh-app-token-passability-test'
		}

		try:
			with request.urlopen(request.Request(api_url, headers=headers)) as response:
				payload = json.loads(response.read().decode('utf-8'))
		except error.HTTPError as http_err:
			self.fail(f'GitHub API rejected GH_TOKEN for {target_repo}: HTTP {http_err.code}')

		full_name = payload.get('full_name', '')
		self.assertEqual(
			full_name.lower(),
			target_repo.lower(),
			f'GH_TOKEN can call API but not access expected repo {target_repo}.'
		)


if __name__ == '__main__':
	unittest.main()
