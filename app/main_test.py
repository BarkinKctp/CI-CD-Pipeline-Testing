import unittest

from app import build_packages_test, publish_test, routes_test


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(routes_test))
    suite.addTests(loader.loadTestsFromModule(build_packages_test))
    suite.addTests(loader.loadTestsFromModule(publish_test))
    return suite

if __name__ == '__main__':
    unittest.main()