import time
import unittest
from unitti import after_functions, before_functions, groups, serial, alias, before_aliases, after_aliases, data_provider


def f():
    return [['admin', '123456'], ['admin123', '456']]


class SmokingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        time.sleep(1)
        print('smoking setup class')

    def test_smoking_1(self):
        time.sleep(1)
        print('smoking test 1')

    def test_smoking_2(self):
        time.sleep(1)
        print('smoking test 2')
        # assert False, 'smoking test 2 fail'

    @groups('P0', 'P1')
    def test_smoking_3(self):
        time.sleep(1)
        print('smoking test 3')

    @groups('P0')
    @data_provider(f, ('dataset#1', 'dataset#2'))
    def test_smoking_4(self, username, password):
        time.sleep(1)
        print('smoking test 4 | {0}: {1}'.format(username, password))

    @classmethod
    def tearDownClass(cls):
        print('smoking teardown class')


# @serial(definition_order=True, fast_fail=True)
@serial(definition_order=True)
class RegressionTests(unittest.TestCase):
    def test_regression_4(self):
        time.sleep(1)
        print('regression test 4')

    def test_regression_3(self):
        time.sleep(1)
        print('regression test 3')

    def test_regression_2(self):
        time.sleep(1)
        print('regression test 2')

    def test_regression_1(self):
        time.sleep(1)
        print('regression test 1')


# class E2ETests(unittest.TestCase):
#     def test_e2e_base(self):
#         time.sleep(1)
#         print('e2e test base')
#
#     def test_e2e_extend(self):
#         time.sleep(1)
#         print('e2e test extend')
#         # assert False, 'test_e2e_extend fail'
#
#     def test_e2e_minor(self):
#         time.sleep(1)
#         print('e2e test minor')
#
#     def test_e2e_extra(self):
#         time.sleep(1)
#         print('e2e test extra')
