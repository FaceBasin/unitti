from example import testcases
from unitti import load_classes
from extension.uti_html_test_runner import HTMLTestRunner

s = load_classes(
    testcases.SmokingTests,
    testcases.RegressionTests,
    # testcases.E2ETests,
    include=['P0'],
    exclude=['P1']
)

f = open('report.html', 'wb')
runner = HTMLTestRunner(stream=f, title='Test Report Example',
                        description='This is a report example generated with UnitTi and custom HTMLTestRunner')
runner.run(s)
