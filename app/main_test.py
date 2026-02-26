import unittest
import os
from unittest.mock import patch

from app.main import app

class TestMain(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()