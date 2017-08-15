import pytest

from nuts.data.test_suite import TestSuite as TSuite
from nuts.service.evaluator import Evaluator


@pytest.fixture
def test_suite():
    test_suite = TSuite('TestTestSuite')
    data = [
        {'name': 'testPingFromAToB',
         'command': 'connectivity',
         'devices': 'Server01',
         'parameter': '8.8.8.8',
         'operator': '=',
         'expected': 'True'
         },
        {'name': 'checkuser',
         'command': 'checkuser',
         'devices': 'Server01',
         'parameter': '8.8.8.8',
         'operator': '=',
         'expected': ['admin', 'user']
         },
        {'name': 'Count ospf neighbors',
         'command': 'countospfneighbors',
         'devices': 'Switch1',
         'parameter': '',
         'operator': '=',
         'expected': '3'
         },
        {'name': 'checkuser multiple devices',
         'command': 'checkuser',
         'devices': 'cisco.*',
         'parameter': '',
         'operator': '=',
         'expected': ['admin', 'user']
         }
    ]
    for d in data:
        test_suite.create_test(**d)
    return test_suite


@pytest.fixture
def evaluator(test_suite):
    return Evaluator(test_suite)


def test_comp_multiple_devices(test_suite, evaluator):
    test_case = test_suite.get_test_by_name('checkuser multiple devices')
    result = {
        u'cisco.csr.1000v': {'resulttype': 'single', 'result': ['admin', 'user']},
        u'cisco.test': {'resulttype': 'single', 'result': ['admin', 'user']}
    }
    test_case.minions = [u'cisco.csr.1000v', u'cisco.test']
    test_case.actual_result = result
    assert evaluator.compare(test_case).result() is True


def test_comp_multiple_devices_false(test_suite, evaluator):
    test_case = test_suite.get_test_by_name('checkuser multiple devices')
    result = {
        u'cisco.csr.1000v': {'resulttype': 'single', 'result': ['admin', 'user']},
        u'cisco.test': {'resulttype': 'single', 'result': ['admin']}
    }
    test_case.minions = [u'cisco.csr.1000v', u'cisco.test']
    test_case.actual_result = result
    assert evaluator.compare(test_case).result() is False


def test_comp_multiple(evaluator):
    list1 = []
    list2 = []
    list1.append('admin')
    list1.append('user')
    list2.append('user')
    list2.append('admin')
    assert evaluator.comp(list1, list2) is True


def test_comp_multiple_false(evaluator):
    list1 = []
    list2 = []
    list1.append('admin')
    list1.append('user')
    list2.append('user')
    assert evaluator.comp(list1, list2) is False


def test_compare_single_true(test_suite, evaluator):
    test_case = test_suite.get_test_by_name('Count ospf neighbors')
    result = {u'cisco.csr.1000v': {'resulttype': 'single', 'result': '3'}}
    test_case.minions.append('cisco.csr.1000v')
    test_case.actual_result = result
    evaluation = evaluator.compare(test_case)
    assert evaluation.expected_result == '3'
    assert len(evaluation.evaluation_results) == 1
    assert evaluation.result() is True


def test_compare_single_false(test_suite, evaluator):
    result = {u'cisco.csr.1000v': {'resulttype': 'single', 'result': 'False'}}
    test_case = test_suite.get_test_by_name('testPingFromAToB')
    test_case.minions.append('cisco.csr.1000v')
    test_case.actual_result = result
    assert evaluator.compare(test_case).result() is False


def test_compare_multiple_true(test_suite, evaluator):
    result = {u'cisco.csr.1000v': {'resulttype': 'multiple', 'result': ['admin', 'user']}}
    test_case = test_suite.get_test_by_name('checkuser')
    test_case.minions.append('cisco.csr.1000v')
    test_case.actual_result = result
    assert evaluator.compare(test_case).result() is True


def test_compare_multiple_false(test_suite, evaluator):
    result = {u'cisco.csr.1000v': {'resulttype': 'multiple', 'result': ['admin']}}
    test_case = test_suite.get_test_by_name('checkuser')
    test_case.minions.append('cisco.csr.1000v')
    test_case.actual_result = result
    assert evaluator.compare(test_case).result() is False
