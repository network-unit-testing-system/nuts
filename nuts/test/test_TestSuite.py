import pytest
from src.data.TestSuite import TestSuite


@pytest.fixture
def test_suite():
    test_suite = TestSuite("TestTestSuite")
    test_suite.create_test("testPingFromAToB", "connectivity", 'Server01', '8.8.8.8', "=", 'True')
    test_suite.create_test("checkuser", "checkuser", 'Server02', '8.8.8.8', "=", 'admin')
    test_suite.create_test("Count ospf neighbors", "countospfneighbors", 'Switch1', '', "=", '3')
    return test_suite


class TestTestSuite:

    def test_get_test_by_name_not_found(self, test_suite):
        assert test_suite.get_test_by_name("no such test") is None

    def test_get_test_by_name_first(self, test_suite):
        assert test_suite.get_test_by_name("testPingFromAToB") is not None
        assert test_suite.get_test_by_name("testPingFromAToB").name == "testPingFromAToB"
        assert test_suite.get_test_by_name("testPingFromAToB").command == "connectivity"

    def test_get_test_by_name_not_first(self, test_suite):
        assert test_suite.get_test_by_name("checkuser") is not None
        assert test_suite.get_test_by_name("checkuser").name == "checkuser"
        assert test_suite.get_test_by_name("checkuser").command == "checkuser"

    def test_get_test_by_name_last(self, test_suite):
        assert test_suite.get_test_by_name("Count ospf neighbors") is not None
        assert test_suite.get_test_by_name("Count ospf neighbors").name == "Count ospf neighbors"
        assert test_suite.get_test_by_name("Count ospf neighbors").command == "countospfneighbors"
