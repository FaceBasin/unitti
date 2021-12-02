import time
import unittest
from unitti import load_classes, alias, before_aliases


r1, r2, r3, r4 = [], [], [], []
e1 = e2 = e4 = ['test2', 'test1']
e3 = ['test2']


class TestAA1A(unittest.TestCase):
    @alias('a1')
    def test1(self):
        r1.append('test1')


class TestAA1B(unittest.TestCase):
    @before_aliases('a1')
    def test2(self):
        time.sleep(0.1)
        r1.append('test2')


class TestAA2A(unittest.TestCase):
    @alias('a2')
    def test1(self):
        r2.append('test1')


class TestAA2B(unittest.TestCase):
    @before_aliases('a2', hard_dependency=False)
    def test2(self):
        time.sleep(0.1)
        r2.append('test2')


class TestAA3A(unittest.TestCase):
    @alias('a3')
    def test1(self):
        r3.append('test1')


class TestAA3B(unittest.TestCase):
    @before_aliases('a3')
    def test2(self):
        time.sleep(0.1)
        r3.append('test2')
        assert False


class TestAA4A(unittest.TestCase):
    @alias('a4')
    def test1(self):
        r4.append('test1')


class TestAA4B(unittest.TestCase):
    @before_aliases('a4', hard_dependency=False)
    def test2(self):
        time.sleep(0.1)
        r4.append('test2')
        assert False


runner = unittest.TextTestRunner()

s = load_classes(
    TestAA1A,
    TestAA1B,
    TestAA2A,
    TestAA2B,
    TestAA3A,
    TestAA3B,
    TestAA4A,
    TestAA4B,
)

runner.run(s)

assert r1 == e1, r1
assert r2 == e2, r2
assert r3 == e3, r3
assert r4 == e4, r4

print('success')
