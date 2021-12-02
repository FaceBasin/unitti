import time
import unittest
from unitti import load_classes, groups, before_groups


r1, r2, r3, r4 = [], [], [], []
e1 = e2 = e4 = ['test2', 'test1']
e3 = ['test2']


class TestAG1A(unittest.TestCase):
    @groups('G1')
    def test1(self):
        r1.append('test1')


class TestAG1B(unittest.TestCase):
    @before_groups('G1')
    def test2(self):
        time.sleep(0.1)
        r1.append('test2')


class TestAG2A(unittest.TestCase):
    @groups('G2')
    def test1(self):
        r2.append('test1')


class TestAG2B(unittest.TestCase):
    @before_groups('G2', hard_dependency=False)
    def test2(self):
        time.sleep(0.1)
        r2.append('test2')


class TestAG3A(unittest.TestCase):
    @groups('G3')
    def test1(self):
        r3.append('test1')


class TestAG3B(unittest.TestCase):
    @before_groups('G3')
    def test2(self):
        time.sleep(0.1)
        r3.append('test2')
        assert False


class TestAG4A(unittest.TestCase):
    @groups('G4')
    def test1(self):
        r4.append('test1')


class TestAG4B(unittest.TestCase):
    @before_groups('G4', hard_dependency=False)
    def test2(self):
        time.sleep(0.1)
        r4.append('test2')
        assert False


runner = unittest.TextTestRunner()

s = load_classes(
    TestAG1A,
    TestAG1B,
    TestAG2A,
    TestAG2B,
    TestAG3A,
    TestAG3B,
    TestAG4A,
    TestAG4B,
)

runner.run(s)

assert r1 == e1, r1
assert r2 == e2, r2
assert r3 == e3, r3
assert r4 == e4, r4

print('success')
