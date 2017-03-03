import pytest
from src.data.TestSuite import TestSuite


class TestTestSuite:
    test_suite = TestSuite("TestTestSuite")

    @classmethod
    def setup_class(cls):
        cls.test_suite.create_test("testPingFromAToB", "connectivity", 'Server01', '8.8.8.8', "=", 'True')
        cls.test_suite.create_test("checkuser", "checkuser", 'Server02', '8.8.8.8', "=", 'admin')
        cls.test_suite.create_test("Count ospf neighbors", "countospfneighbors", 'Switch1', '', "=", '3')

    def test_get_test_by_name_not_found(self):
        assert self.test_suite.get_test_by_name("no such test") is None

    def test_get_test_by_name_first(self):
        assert self.test_suite.get_test_by_name("testPingFromAToB") is not None
        assert self.test_suite.get_test_by_name("testPingFromAToB").name == "testPingFromAToB"
        assert self.test_suite.get_test_by_name("testPingFromAToB").command == "connectivity"

    def test_get_test_by_name_not_first(self):
        assert self.test_suite.get_test_by_name("checkuser") is not None
        assert self.test_suite.get_test_by_name("checkuser").name == "checkuser"
        assert self.test_suite.get_test_by_name("checkuser").command == "checkuser"

    def test_get_test_by_name_last(self):
        assert self.test_suite.get_test_by_name("Count ospf neighbors") is not None
        assert self.test_suite.get_test_by_name("Count ospf neighbors").name == "Count ospf neighbors"
        assert self.test_suite.get_test_by_name("Count ospf neighbors").command == "countospfneighbors"
