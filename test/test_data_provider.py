import unittest
from unitti import load_classes, groups, data_provider
from extension.uti_html_test_runner import HTMLTestRunner


def dp():
    return [
        ['aa', '11'],
        ['bb', '22'],
        ['cc', '33']
    ]


r1, r2, r3, r4, r5, r6, r7 = [], [], [], [], [], [], []
e1 = e7 = ['aa11', 'bb22', 'cc33']
e2 = ['aa11', 'bb22']
e3 = e4 = ['aa11']
e5 = ['aa11', 'bb22', 'cc33']
e6 = ['aa11']


class TestDP1(unittest.TestCase):
    @data_provider(dp, ['D1', 'D2', 'D3'], [['P0'], ['P1'], ['P2']])
    def test1(self, x, y):
        print('test1')
        r1.append(x+y)


# exclude
class TestDP2(unittest.TestCase):
    @data_provider(dp, ['D1', 'D2', 'D3'], [['P0'], ['P1'], ['P2']])
    def test1(self, x, y):
        r2.append(x+y)


# include and exclude
class TestDP3(unittest.TestCase):
    @data_provider(dp, ['D1', 'D2', 'D3'], [['P0'], ['P1'], ['P2']])
    def test1(self, x, y):
        r3.append(x+y)


class TestDP4(unittest.TestCase):
    # include
    @data_provider(dp, ['D1', 'D2', 'D3'], [['P0'], ['P1'], ['P2']])
    def test1(self, x, y):
        r4.append(x+y)

    # default group include
    @groups('P0')
    @data_provider(dp, ['D1', 'D2', 'D3'])
    def test2(self, x, y):
        r5.append(x+y)

    # appended group include
    @groups('P1')
    @data_provider(dp, ['D1', 'D2', 'D3'], [['P0'], ['P1'], ['P2']])
    def test3(self, x, y):
        r6.append(x+y)

    # appended group include 2
    @groups('P0')
    @data_provider(dp, ['D1', 'D2', 'D3'], [['P0'], ['P1'], ['P2']])
    def test4(self, x, y):
        r7.append(x+y)


f = open('report.html', 'wb')
runner = HTMLTestRunner(stream=f, title='Test Report Example',
                        description='This is a report example generated with UnitTi and custom HTMLTestRunner')

s1 = load_classes(TestDP1)
s2 = load_classes(TestDP2, exclude=['P2'])
s3 = load_classes(TestDP3, include=['P0'], exclude=['P2'])
s4 = load_classes(TestDP4, include=['P0'])

runner.run(s1, s2, s3, s4)

assert r1 == e1, r1
assert r2 == e2, r2
assert r3 == e3, r3
assert r4 == e4, r4
assert r5 == e5, r5
assert r6 == e6, r6
assert r7 == e7, r7

print('success')
