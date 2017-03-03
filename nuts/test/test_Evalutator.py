import pytest
from src.service.Evaluator import Evaluator
from src.data.TestSuite import TestSuite


class TestTestSuite:
    test_suite = TestSuite("TestTestSuite")
    eval = Evaluator(test_suite)

    @classmethod
    def setup_class(cls):
        cls.test_suite.create_test("testPingFromAToB", "connectivity", 'Server01', '8.8.8.8', "=", 'True')
        cls.test_suite.create_test("checkuser", "checkuser", 'Server02', '8.8.8.8', "=", 'admin')
        cls.test_suite.create_test("Count ospf neighbors", "countospfneighbors", 'Switch1', '', "=", '3')
        cls.eval = Evaluator(cls.test_suite)

    def test_comp_multiple(self):
        list1 = []
        list2 = []
        list1.append('admin')
        list1.append('user')
        list2.append('user')
        list2.append('admin')
        self.eval.comp(list1, list2) is True

    def test_comp_multiple_false(self):
        list1 = []
        list2 = []
        list1.append('admin')
        list1.append('user')
        list2.append('user')
        self.eval.comp(list1, list2) is False

    def test_compare_single_true(self):
        test_case = self.test_suite.get_test_by_name('Count ospf neighbors')
        result = {"resulttype": "single", "result": '3'}
        test_case.actual_result = result
        self.eval.compare(test_case) is 3

    def test_compare_single_false(self):
        result = {"resulttype": "single", "result": 'False'}
        test_case = self.test_suite.get_test_by_name('testPingFromAToB')
        test_case.actual_result = result
        self.eval.compare(test_case) is False

    def test_compare_multiple_true(self):
        result = {"resulttype": "multiple", "result": ['admin', 'user']}
        test_case = self.test_suite.get_test_by_name('checkuser')
        test_case.actual_result = result
        self.eval.compare(test_case) is True

    def test_compare_multiple_false(self):
        result = {"resulttype": "multiple", "result": ['admin']}
        test_case = self.test_suite.get_test_by_name('checkuser')
        test_case.actual_result = result
        self.eval.compare(test_case) is False
