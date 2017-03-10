import pytest
from src.service.Evaluator import Evaluator
from src.data.TestSuite import TestSuite


class TestTestSuite:
    test_suite = TestSuite("TestTestSuite")
    eval = Evaluator(test_suite)

    @classmethod
    def setup_class(cls):
        cls.test_suite.create_test("testPingFromAToB", "connectivity", 'Server01', '8.8.8.8', "=", 'True')
        cls.test_suite.create_test("checkuser", "checkuser", 'Server02', '', "=", ['admin', 'user'])
        cls.test_suite.create_test("Count ospf neighbors", "countospfneighbors", 'Switch1', '', "=", '3')
        cls.test_suite.create_test("checkuser multiple devices", "checkuser", 'cisco.*', '', "=", ['admin', 'user'])

        cls.eval = Evaluator(cls.test_suite)

    def test_comp_multiple_devices(self):
        test_case = self.test_suite.get_test_by_name('checkuser multiple devices')
        result = {
            u'cisco.csr.1000v': {"resulttype": "single", "result": ['admin', 'user']},
            u'cisco.test': {"resulttype": "single", "result": ['admin', 'user']}
        }
        test_case.minions = [u'cisco.csr.1000v', u'cisco.test']
        test_case.actual_result = result
        assert self.eval.compare(test_case).result() is True

    def test_comp_multiple_devices_false(self):
        test_case = self.test_suite.get_test_by_name('checkuser multiple devices')
        result = {
            u'cisco.csr.1000v': {"resulttype": "single", "result": ['admin', 'user']},
            u'cisco.test': {"resulttype": "single", "result": ['admin']}
        }
        test_case.minions = [u'cisco.csr.1000v', u'cisco.test']
        test_case.actual_result = result
        assert self.eval.compare(test_case).result() is False

    def test_comp_multiple(self):
        list1 = []
        list2 = []
        list1.append('admin')
        list1.append('user')
        list2.append('user')
        list2.append('admin')
        assert self.eval.comp(list1, list2) is True

    def test_comp_multiple_false(self):
        list1 = []
        list2 = []
        list1.append('admin')
        list1.append('user')
        list2.append('user')
        assert self.eval.comp(list1, list2) is False

    def test_compare_single_true(self):
        test_case = self.test_suite.get_test_by_name('Count ospf neighbors')
        result = {u'cisco.csr.1000v': {"resulttype": "single", "result": '3'}}
        test_case.minions.append('cisco.csr.1000v')
        test_case.actual_result = result
        evaluation = self.eval.compare(test_case)
        assert evaluation.expected_result == '3'
        assert len(evaluation.evaluation_results) == 1
        assert evaluation.result() is True

    def test_compare_single_false(self):
        result = {u'cisco.csr.1000v': {"resulttype": "single", "result": 'False'}}
        test_case = self.test_suite.get_test_by_name('testPingFromAToB')
        test_case.minions.append('cisco.csr.1000v')
        test_case.actual_result = result
        assert self.eval.compare(test_case).result() is False

    def test_compare_multiple_true(self):
        result = {u'cisco.csr.1000v': {"resulttype": "multiple", "result": ['admin', 'user']}}
        test_case = self.test_suite.get_test_by_name('checkuser')
        test_case.minions.append('cisco.csr.1000v')
        test_case.actual_result = result
        assert self.eval.compare(test_case).result() is True

    def test_compare_multiple_false(self):
        result = {u'cisco.csr.1000v': {"resulttype": "multiple", "result": ['admin']}}
        test_case = self.test_suite.get_test_by_name('checkuser')
        test_case.minions.append('cisco.csr.1000v')
        test_case.actual_result = result
        assert self.eval.compare(test_case).result() is False
