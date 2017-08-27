import pytest
from mock import Mock
from mock import patch

from nuts.data.test_suite import TestSuite as TSuite
from nuts.service.runner import Runner
from nuts.service.salt_api_wrapper import SaltApi


@pytest.fixture
def example_testsuite():
    test_suite = TSuite('ExampleSuite')
    data = [
        {'name': 'testPingFromAToB',
         'command': 'connectivity',
         'devices': 'Server01',
         'parameter': ['8.8.8.8'],
         'operator': '=',
         'expected': 'True'
         },
        {'name': 'checkuser',
         'command': 'checkuser',
         'devices': 'Server01',
         'parameter': ['8.8.8.8'],
         'operator': '=',
         'expected': 'admin'
         },
        {'name': 'Count ospf neighbors',
         'command': 'countospfneighbors',
         'devices': 'Switch1',
         'parameter': [],
         'operator': '=',
         'expected': '3'
         },
        {'name': 'bandwidth test',
         'command': 'bandwidth',
         'devices': 'linux1',
         'parameter': ['10.10.10.10'],
         'operator': '<',
         'expected': '100000000',
         'setup': [
             {'command': 'cmd.run',
              'devices': 'linux2',
              'parameter': ['iperf3 -s -D -1']
              },
             {'command': 'network.ip_addrs',
              'devices': 'linux2',
              'save': 'ip'
              }
         ],
         'teardown': [
             {'command': 'cmd.run',
              'devices': 'linux2',
              'parameter': ['pkill iperf3']
              }
         ]
         }
    ]
    for d in data:
        test_suite.create_test(**d)
    return test_suite


@pytest.fixture
def mock_testsuite():
    mock = Mock(spec=TSuite)
    return mock


@pytest.fixture
def api_mock():
    mock = Mock(spec=SaltApi)
    mock.start_task.return_value = {
        'return': [{'cisco.csr.1000v': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'}}]}
    mock.start_task_async.return_value = {
        'return': [{'jid': '20170302070941729675', 'minions': ['cisco.csr.1000v']}]}
    mock.get_task_result.return_value = {
        'return': [{'cisco.csr.1000v': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'}}]}
    return mock


def test_run_all_sync(example_testsuite, api_mock):
    example_testsuite.test_cases_sync += example_testsuite.test_cases_async
    example_testsuite.test_cases_async = []
    with patch.object(Runner, '_start_test_sync') as run_method_mocked:
        Runner(example_testsuite, api_mock).run_all()
        api_mock.connect.assert_called()
        run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('testPingFromAToB'))
        run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('checkuser'))
        run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('Count ospf neighbors'))
        run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('bandwidth test'))


def test_run_all_async(example_testsuite, api_mock):
    example_testsuite.test_cases_async += example_testsuite.test_cases_sync
    example_testsuite.test_cases_sync = []
    with patch.object(Runner, '_start_test_async') as run_method_mocked:
        with patch.object(Runner, '_collect_result') as result_method_mocked:
            Runner(example_testsuite, api_mock).run_all()
            api_mock.connect.assert_called()
            run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('testPingFromAToB'))
            run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('checkuser'))
            run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('Count ospf neighbors'))
            run_method_mocked.assert_any_call(example_testsuite.get_test_by_name('bandwidth test'))
            result_method_mocked.assert_any_call(example_testsuite.get_test_by_name('testPingFromAToB'))
            result_method_mocked.assert_any_call(example_testsuite.get_test_by_name('checkuser'))
            result_method_mocked.assert_any_call(example_testsuite.get_test_by_name('Count ospf neighbors'))
            result_method_mocked.assert_any_call(example_testsuite.get_test_by_name('bandwidth test'))


def test_run_setup_teardown_sync(api_mock):
    test_suite = TSuite('TestTestSuite')
    test_suite.create_test(name='test', command='testcmd', devices='sw01', parameter='', operator='=', expected=True,
                           setup=[{'command': 'test setup cmd'}], teardown=[{'command': 'test setup cmd'}])
    with patch.object(Runner, '_start_tasks') as start_task_method_mocked:
        Runner(test_suite, api_mock).run_all()
        start_task_method_mocked.assert_any_call(test_suite.test_cases_sync[0].setup_tasks)
        start_task_method_mocked.assert_any_call(test_suite.test_cases_sync[0].teardown_tasks)


def test_run_setup_teardown_async(api_mock):
    test_suite = TSuite('TestTestSuite')
    test_suite.create_test(name='test', command='testcmd', devices='sw01', parameter='', operator='=', expected=True,
                           setup=[{'command': 'test setup cmd'}], teardown=[{'command': 'test setup cmd'}], async=True)
    with patch.object(Runner, '_start_tasks') as start_task_method_mocked:
        Runner(test_suite, api_mock).run_all()
        start_task_method_mocked.assert_any_call(test_suite.test_cases_async[0].setup_tasks)
        start_task_method_mocked.assert_any_call(test_suite.test_cases_async[0].teardown_tasks)


def test_return_setup(api_mock):
    test_suite = TSuite('TestTestSuite')
    test_suite.create_test(name='test', command='testcmd', devices='sw01', parameter='', operator='=', expected=True,
                           setup=[{'command': 'test setup cmd', 'devices': 'sw99', 'save': 'ip'}])
    with patch.object(Runner, '_get_task_result') as create_task_method_mocked:
        Runner(test_suite, api_mock).run_all()
        test_case = test_suite.test_cases_sync[0]
        saved_data = {'ip': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'}}
        create_task_method_mocked.assert_any_call(test_case, saved_data)


def test_start_task(example_testsuite, api_mock):
    runner = Runner(example_testsuite, api_mock)
    test_case = example_testsuite.get_test_by_name('testPingFromAToB')
    runner._start_test_async(test_case)
    api_mock.start_task_async.assert_called_with(
            runner.create_test_task(test_case.devices, test_case.command, test_case.parameter))
    assert test_case.job_id == u'20170302070941729675'


def test_collect_result(example_testsuite, api_mock):
    runner = Runner(example_testsuite, api_mock)
    test_case = example_testsuite.get_test_by_name('testPingFromAToB')
    test_case.job_id = u'20170302070941729675'
    runner._collect_result(test_case)
    api_mock.get_task_result.assert_called_with(taskid=u'20170302070941729675')
    assert test_case.get_actual_result() == {
        u'cisco.csr.1000v': {
            'resulttype': 'single',
            'result': '00:0C:29:EA:D1:68'
        }}


def test_run(example_testsuite, api_mock):
    runner = Runner(example_testsuite, api_mock)
    test_case = example_testsuite.get_test_by_name('testPingFromAToB')
    runner._start_test_sync(test_case)
    api_mock.start_task.assert_called_with(
            runner.create_test_task(test_case.devices, test_case.command, test_case.parameter))
    assert test_case.get_actual_result() == {
        u'cisco.csr.1000v': {
            'resulttype': 'single',
            'result': '00:0C:29:EA:D1:68'
        }}


def test_extract_return_multiple_devices():
    return_dict = {'return': [{'cisco.csr.1000v': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'},
                               'cisco.test': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'}}]}
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
    return_dict = {'return': [{'cisco.csr.1000v': {'resulttype': 'single', 'result': '00:0C:29:EA:D1:68'}}]}
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
    test_case = example_testsuite.get_test_by_name('testPingFromAToB')
    task = runner.create_test_task(test_case.devices, test_case.command, test_case.parameter)
    assert 'targets' in task
    assert 'function' in task
    assert 'arguments' in task
    assert task['targets'] == 'Server01'
    assert task['function'] == 'nuts.connectivity'
    assert task['arguments'] == ['8.8.8.8']


def test_create_task_render():
    task = Runner.create_test_task(devices='sw01{{ id }}', command='test.{{cmd}}',
                                   parameter=['{{ par }}', 'test2 {{ par2 }}'],
                                   render_data={'id': 123, 'cmd': 'command', 'par': 'parameter', 'par2': 2})
    assert 'targets' in task
    assert 'function' in task
    assert 'arguments' in task
    assert task['targets'] == 'sw01123'
    assert task['function'] == 'test.command'
    assert task['arguments'] == ['parameter', 'test2 2']


def test_create_task_add_nuts():
    task = Runner.create_test_task(devices='sw01', command='test')

    assert 'function' in task
    assert task['function'] == 'nuts.test'
