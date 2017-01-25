import pytest
from src.data.Device import Device
from src.data.TestSuite import TestSuite


class TestTestSuite:
    testSuite = TestSuite("TestTestSuite")

    @classmethod
    def setup_class(cls):
        cls.testSuite.createTest("testPingFromAToB", "connectivity", 'Server01', '8.8.8.8', "=", 'True')
        cls.testSuite.createTest("checkuser", "checkuser", 'Server02', '8.8.8.8', "=", 'admin')
        cls.testSuite.createTest("Count ospf neighbors", "countospfneighbors", 'Switch1', '', "=", '3')

    def test_getTestByName_NotFound(self):
        assert self.testSuite.getTestByName("no such test") is None

    def test_getTestByName_First(self):
        assert self.testSuite.getTestByName("testPingFromAToB") is not None
        assert self.testSuite.getTestByName("testPingFromAToB").name == "testPingFromAToB"
        assert self.testSuite.getTestByName("testPingFromAToB").command == "connectivity"

    def test_getTestByName_NotFirst(self):
        assert self.testSuite.getTestByName("checkuser") is not None
        assert self.testSuite.getTestByName("checkuser").name == "checkuser"
        assert self.testSuite.getTestByName("checkuser").command == "checkuser"

    def test_getTestByName_Last(self):
        assert self.testSuite.getTestByName("Count ospf neighbors") is not None
        assert self.testSuite.getTestByName("Count ospf neighbors").name == "Count ospf neighbors"
        assert self.testSuite.getTestByName("Count ospf neighbors").command == "countospfneighbors"
