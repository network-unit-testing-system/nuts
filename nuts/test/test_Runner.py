import pytest
from mock import Mock
from mock import patch
from src.service.salt_api_wrapper import SaltApi
from src.service.Runner import Runner
from src.data.TestSuite import TestSuite
@pytest.fixture
def example_testsuite():
    testsuite = TestSuite("ExampleSuite")
    testsuite.createTest("testPingFromAToB", "connectivity", 'Server01', '8.8.8.8', "=", 'True')
    testsuite.createTest("checkuser", "checkuser", 'Server02', '8.8.8.8', "=", 'admin')
    testsuite.createTest("Count ospf neighbors", "countospfneighbors", 'Switch1', '', "=", '3')
    return testsuite
@pytest.fixture
def mock_testsuite():
    mock = Mock(spec=TestSuite)
    return mock
@pytest.fixture
def api_mock():
    mock = Mock(spec=SaltApi)
    mock.start_task.return_value = {u'return': [{u'cisco.csr.1000v': u'{"resulttype": "single", "result": "000c.29ea.d168"}'}]}
    return mock

class TestRunner:
    def test_run_all(self,example_testsuite, api_mock):
        with patch.object(Runner, "run") as runmethod_mocked:
            Runner(example_testsuite,api_mock).run_all()
            runmethod_mocked.assert_any_call(example_testsuite.getTestByName("testPingFromAToB"))
            runmethod_mocked.assert_any_call(example_testsuite.getTestByName("checkuser"))
            runmethod_mocked.assert_any_call(example_testsuite.getTestByName("Count ospf neighbors"))
        
    def test_run(self,example_testsuite, api_mock):
        runner = Runner(example_testsuite, api_mock)
        test_case = example_testsuite.getTestByName("testPingFromAToB")
        runner.run(test_case)
        api_mock.connect.assert_called()
        api_mock.start_task.assert_called_with(runner.create_task(test_case))
        assert example_testsuite.getActualResult(test_case) == {
            "resulttype": "single",
             "result": "000c.29ea.d168"
        }
    
    def test_extractReturn(self):
        returnDict = {u'return': [{u'cisco.csr.1000v': u'{"resulttype": "single", "result": "000c.29ea.d168"}'}]}
        assert Runner._extractReturn(returnDict) == {
            'resulttype':'single',
            'result':'000c.29ea.d168'
        }
    
    def test_extractReturnEmpty(self):
        returnDict = {u'return': [{u'cisco.csr.1000v': None}]}
        assert Runner._extractReturn(returnDict) == {
                    'resulttype':'single',
                    'result':None
        }
    def test_create_task(self, example_testsuite, api_mock):
        runner = Runner(example_testsuite,api_mock)
        task = runner.create_task(example_testsuite.getTestByName("testPingFromAToB"))
        assert 'targets' in task
        assert 'function' in task
        assert 'arguments' in task
        assert task['targets'] == 'Server01'
        assert task['function'] == 'nuts.connectivity'
        assert task['arguments'] == '8.8.8.8'
