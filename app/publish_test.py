import unittest

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


if __name__ == '__main__':
	unittest.main()
