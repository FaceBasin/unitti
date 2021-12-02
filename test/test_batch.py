import time
import unittest
from unitti import load_classes, batch


e1 = ['A', 'B', 'C', 'D']
e2 = ['A', 'C', 'B', 'D']
r = []


# batch = 0
@batch(0)
class TestA(unittest.TestCase):
    def test1(self):
        r.append('A')
        time.sleep(0.1)


# default batch
class TestB(unittest.TestCase):
    def test1(self):
        r.append('B')
        time.sleep(0.1)


# batch = 4
@batch(4)
class TestC(unittest.TestCase):
    def test1(self):
        r.append('C')
        time.sleep(0.1)


# batch = 8
@batch(8)
class TestD(unittest.TestCase):
    def test1(self):
        r.append('D')
        time.sleep(0.1)


runner = unittest.TextTestRunner()

s = load_classes(
    TestD,
    TestC,
    TestB,
    TestA
)

runner.run(s)

assert r == e1 or r == e2, r

print('success')
