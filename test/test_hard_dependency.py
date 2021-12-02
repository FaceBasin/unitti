import unittest
from unitti import load_classes, after_functions, before_functions


res = []


class TestHD(unittest.TestCase):
    def test1(self):
        assert False

    @before_functions('test3', hard_dependency=False)
    @after_functions('test1', hard_dependency=True)
    def test2(self):
        res.append('test2')

    def test3(self):
        res.append('test3')


runner = unittest.TextTestRunner()
s = load_classes(TestHD)
runner.run(s)
assert res == ['test3'], res
print('success')
