import pytest
from mock import Mock
from mock import patch

from nuts.data.test_suite import TestSuite as TSuite
from nuts.service.runner import Runner
from nuts.service.salt_api_wrapper import SaltApi


@pytest.fixture
def example_testsuite():
    test_suite = TSuite('ExampleSuite')
    test_suite.create_test('testPingFromAToB', 'connectivity', 'Server01', '8.8.8.8', '=', 'True')
    test_suite.create_test('checkuser', 'checkuser', 'Server02', '8.8.8.8', '=', 'admin')
    test_suite.create_test('Count ospf neighbors', 'countospfneighbors', 'Switch1', '', '=', '3')
    return test_suite


@pytest.fixture
def mock_testsuite():
    mock = Mock(spec=TSuite)
    return mock


@pytest.fixture
def api_mock():
    mock = Mock(spec=SaltApi)
    mock.start_task.return_value = {
        u'return': [{u'cisco.csr.1000v': u'{"resulttype": "single", "result": "00:0C:29:EA:D1:68"}'}]}
    mock.start_task_async.return_value = {
        u'return': [{u'jid': u'20170302070941729675', u'minions': [u'cisco.csr.1000v']}]}
    mock.get_task_result.return_value = {
        u'return': [{u'cisco.csr.1000v': u'{"resulttype": "single", "result": "00:0C:29:EA:D1:68"}'}]}
    return mock


def test_run_all_sync(example_testsuite, api_mock):
    with patch.object(Runner, 'run') as run_method_mocked:
        Runner(example_testsuite, api_mock).run_all(execute_async=False)
        run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('testPingFromAToB'))
        run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('checkuser'))
        run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('Count ospf neighbors'))


def test_run_all_async(example_testsuite, api_mock):
    with patch.object(Runner, '_start_task') as run_method_mocked:
        with patch.object(Runner, '_collect_result') as result_method_mocked:
            Runner(example_testsuite, api_mock).run_all(execute_async=True)
            run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('testPingFromAToB'))
            run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('checkuser'))
            run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('Count ospf neighbors'))
            result_method_mocked.assert_any_call(example_testsuite.get_test_by_name('testPingFromAToB'))
            result_method_mocked.assert_any_call(example_testsuite.get_test_by_name('checkuser'))
            result_method_mocked.assert_any_call(example_testsuite.get_test_by_name('Count ospf neighbors'))


def test_start_task(example_testsuite, api_mock):
    runner = Runner(example_testsuite, api_mock)
    test_case = example_testsuite.get_test_by_name('testPingFromAToB')
    runner._start_task(test_case)
    api_mock.connect.assert_called()
    api_mock.start_task_async.assert_called_with(runner.create_task(test_case))
    assert test_case.job_id == u'20170302070941729675'


def test_collect_result(example_testsuite, api_mock):
    runner = Runner(example_testsuite, api_mock)
    test_case = example_testsuite.get_test_by_name('testPingFromAToB')
    test_case.job_id = u'20170302070941729675'
    runner._collect_result(test_case)
    api_mock.get_task_result.assert_called_with(taskid=u'20170302070941729675')
    assert example_testsuite.get_actual_result(test_case) == {
        u'cisco.csr.1000v': {
            'resulttype': 'single',
            'result': '00:0C:29:EA:D1:68'
        }}


def test_run(example_testsuite, api_mock):
    runner = Runner(example_testsuite, api_mock)
    test_case = example_testsuite.get_test_by_name('testPingFromAToB')
    runner.run(test_case)
    api_mock.connect.assert_called()
    api_mock.start_task.assert_called_with(runner.create_task(test_case))
    assert example_testsuite.get_actual_result(test_case) == {
        u'cisco.csr.1000v': {
            'resulttype': 'single',
            'result': '00:0C:29:EA:D1:68'
        }}


def test_extract_return_multiple_devices():
    return_dict = {u'return': [{u'cisco.csr.1000v': u'{"resulttype": "single", "result": "00:0C:29:EA:D1:68"}',
                                u'cisco.test': u'{"resulttype": "single", "result": "00:0C:29:EA:D1:68"}'}]}
    assert Runner._extract_return(return_dict) == {
        u'cisco.csr.1000v': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'},
        u'cisco.test': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'}
    }


def test_extract_return_empty_multiple_devices():
    return_dict = {u'return': [{u'cisco.csr.1000v': None,
                                u'cisco.test': None}]}
    assert Runner._extract_return(return_dict) == {
        u'cisco.csr.1000v': {'resulttype': 'single', 'result': None},
        u'cisco.test': {'resulttype': 'single', 'result': None}
    }


def test_extract_return():
    return_dict = {u'return': [{u'cisco.csr.1000v': u'{"resulttype": "single", "result": "00:0C:29:EA:D1:68"}'}]}
    assert Runner._extract_return(return_dict) == {
        u'cisco.csr.1000v': {
            'resulttype': 'single',
            'result': '00:0C:29:EA:D1:68'
        }}


def test_extract_return_empty():
    return_dict = {u'return': [{u'cisco.csr.1000v': None}]}
    assert Runner._extract_return(return_dict) == {
        u'cisco.csr.1000v': {
            'resulttype': 'single',
            'result': None
        }}


def test_create_task(example_testsuite, api_mock):
    runner = Runner(example_testsuite, api_mock)
    task = runner.create_task(example_testsuite.get_test_by_name('testPingFromAToB'))
    assert 'targets' in task
    assert 'function' in task
    assert 'arguments' in task
    assert task['targets'] == 'Server01'
    assert task['function'] == 'nuts.connectivity'
    assert task['arguments'] == '8.8.8.8'
