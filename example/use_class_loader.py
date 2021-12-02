import unittest
from example import testcases
from unitti import load_classes

runner = unittest.TextTestRunner()

s = load_classes(
    testcases.SmokingTests,
    testcases.RegressionTests,
    # testcases.E2ETests,
    include=['P0'],
    exclude=['P1']
)

runner.run(s)
