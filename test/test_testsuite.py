import pytest

from nuts.data.test_suite import TestSuite as TSuite


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
         'expected': 'admin'
         },
        {'name': 'Count ospf neighbors',
         'command': 'countospfneighbors',
         'devices': 'Switch1',
         'parameter': '',
         'operator': '=',
         'expected': '3'
         }
    ]
    for d in data:
        test_suite.create_test(**d)
    return test_suite


def test_get_test_by_name_not_found(test_suite):
    assert test_suite.get_test_by_name('no such test') is None


def test_get_test_by_name_first(test_suite):
    assert test_suite.get_test_by_name('testPingFromAToB') is not None
    assert test_suite.get_test_by_name('testPingFromAToB').name == 'testPingFromAToB'
    assert test_suite.get_test_by_name('testPingFromAToB').command == 'connectivity'


def test_get_test_by_name_not_first(test_suite):
    assert test_suite.get_test_by_name('checkuser') is not None
    assert test_suite.get_test_by_name('checkuser').name == 'checkuser'
    assert test_suite.get_test_by_name('checkuser').command == 'checkuser'


def test_get_test_by_name_last(test_suite):
    assert test_suite.get_test_by_name('Count ospf neighbors') is not None
    assert test_suite.get_test_by_name('Count ospf neighbors').name == 'Count ospf neighbors'
    assert test_suite.get_test_by_name('Count ospf neighbors').command == 'countospfneighbors'
