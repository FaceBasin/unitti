import time
import unittest
from unitti import load_classes, groups, default_groups, data_provider, before_groups, after_groups



r1, r2, r3, r4, r5, r6, r7, r8 = [], [], [], [], [], [], [], []
e3 = ['test2']
e2 = []
e1 = ['test2', 'test2']
e4 = e5 = e7 = ['test2', 'test1']
e6 = ['aa11', 'bb22'] or ['bb22', 'aa11']
e8 = ['test1', 'test2']


def dp():
    return [
        ['aa', '11'],
        ['bb', '22'],
        ['cc', '33']
    ]


@default_groups('G0')
class TestAG1A(unittest.TestCase):
    def test1(self):
        r1.append('test1')

    @groups('G3')
    def test2(self):
        r1.append('test2')


class TestAG1B(unittest.TestCase):
    @groups('G1')
    def test2(self):
        time.sleep(0.1)
        r1.append('test2')


class TestAG2A(unittest.TestCase):
    @default_groups('G0')
    def test1(self):
        r2.append('test1')


@default_groups('G0')
@groups('G2')
class TestAG3A(unittest.TestCase):
    def test1(self):
        r3.append('test2')


@default_groups('G4', 'G1')
class TestAG3B(unittest.TestCase):
    def test1(self):
        r3.append('test2')


@groups('G5')
class TestAG4A(unittest.TestCase):  # BUG
    def test1(self):
        r4.append('test1')


class TestAG4B(unittest.TestCase):
    @before_groups('G5')
    def test2(self):
        time.sleep(0.1)
        r4.append('test2')


@default_groups('G6')
class TestAG5A(unittest.TestCase):  # BUG
    def test1(self):
        r5.append('test1')


class TestAG5B(unittest.TestCase):
    @before_groups('G6')
    def test2(self):
        time.sleep(0.1)
        r5.append('test2')


class TestAG6A(unittest.TestCase):
    @default_groups('G7')
    def test1(self):
        r7.append('test1')


class TestAG6B(unittest.TestCase):
    @before_groups('G7')
    def test2(self):
        time.sleep(0.1)
        r7.append('test2')


class TestAG7A(unittest.TestCase):
    @default_groups('G8')
    def test1(self):
        r8.append('test1')


class TestAG7B(unittest.TestCase):
    @after_groups('G8')
    def test2(self):
        time.sleep(0.1)
        r8.append('test2')

# exclude


class TestDP2(unittest.TestCase):
    @data_provider(dp, ['D1', 'D2', 'D3'], [['P0'], ['P1'], ['P2']])
    def test1(self, x, y):
        r6.append(x+y)


runner = unittest.TextTestRunner()
s = load_classes(
    TestAG1A,
    TestAG1B,
    TestAG2A,
    TestAG3A,
    TestAG3B,
    # TestAG4A,
    # TestAG4B,
    # TestAG5A,
    # TestAG5B,
    TestAG6A,
    TestAG6B,
    TestAG7A,
    TestAG7B,
    TestDP2, exclude=["P2", "G0", "G4"]
)


runner.run(s)

assert r1 == e1, r1
assert r2 == e2, r2
assert r3 == e3, r3
# assert r4 == e4, r4
# assert r5 == e5, r5
assert r6 == e6, r6
assert r7 == e7, r7
assert r8 == e8, r8

print('success')
