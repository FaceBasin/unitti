import unittest
from extension.uti_suite_loader import load_test

runner = unittest.TextTestRunner()
suites = load_test('my_test.json')
runner.run(suites[0])
