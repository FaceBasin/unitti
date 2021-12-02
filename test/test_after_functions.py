import time
import unittest
from unitti import load_classes, after_functions


r1, r2, r3, r4 = [], [], [], []
e1 = e2 = e4 = ['cls_setup', 'test2', 'test1', 'cls_td']
e3 = ['cls_setup', 'test2', 'cls_td']


class TestAF1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        time.sleep(0.2)
        r1.append('cls_setup')

    @after_functions('test2')
    def test1(self):
        r1.append('test1')

    def test2(self):
        time.sleep(0.1)
        r1.append('test2')

    @classmethod
    def tearDownClass(cls):
        r1.append('cls_td')


class TestAF2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        time.sleep(0.2)
        r2.append('cls_setup')

    @after_functions('test2', hard_dependency=False)
    def test1(self):
        r2.append('test1')

    def test2(self):
        time.sleep(0.1)
        r2.append('test2')

    @classmethod
    def tearDownClass(cls):
        r2.append('cls_td')


class TestAF3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        time.sleep(0.2)
        r3.append('cls_setup')

    @after_functions('test2')
    def test1(self):
        r3.append('test1')

    def test2(self):
        time.sleep(0.1)
        r3.append('test2')
        assert False

    @classmethod
    def tearDownClass(cls):
        r3.append('cls_td')


class TestAF4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        time.sleep(0.2)
        r4.append('cls_setup')

    @after_functions('test2', hard_dependency=False)
    def test1(self):
        r4.append('test1')

    def test2(self):
        time.sleep(0.1)
        r4.append('test2')
        assert False

    @classmethod
    def tearDownClass(cls):
        r4.append('cls_td')


runner = unittest.TextTestRunner()

s = load_classes(
    TestAF1,
    TestAF2,
    TestAF3,
    TestAF4
)

runner.run(s)

assert r1 == e1, r1
assert r2 == e2, r2
assert r3 == e3, r3
assert r4 == e4, r4

print('success')
