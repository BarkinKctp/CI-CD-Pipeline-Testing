from app.main import return_backwards_string, get_mode
import unittest
import os

# This is a sample test case for the main.py functions
class TestMain(unittest.TestCase):
    def test_return_backwards_string(self):
        random_string = "Hello, World!"
        random_string_backwards = "!dlroW ,olleH"
        self.assertEqual(return_backwards_string
                         (random_string), random_string_backwards)
    def test_get_env(self):
        self.assertEqual(os.environ.get("MODE", get_mode()), "No mode set")

if __name__ == '__main__':
    unittest.main()