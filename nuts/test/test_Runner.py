import pytest
from mock import Mock
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
    mock.start_task.return_value = {'return':[{'cisco.csr.1000v':"123"}]}
    return mock

class TestRunner:
    def test_runAll(self):
        pass
    def test_run(self,example_testsuite, api_mock):
        runner = Runner(example_testsuite, api_mock)
        runner.run(example_testsuite.getTestByName("testPingFromAToB"))
        api_mock.connect.assert_called()

    
    def test_extractReturn(self):
        returnDict = {'return':[{'cisco.csr.1000v':"123"}]}
        assert Runner._extractReturn(returnDict) == "123"
    def test_extractReturnEmpty(self):
        returnDict = {'return':[{'cisco.csr.1000v':None}]}
        assert Runner._extractReturn(returnDict) == None
        