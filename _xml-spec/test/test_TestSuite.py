import pytest
from src.data.Device import Device
from src.data.TestSuite import TestSuite

class TestTestSuite:

    testSuite = TestSuite("TestTestSuite")

    @classmethod
    def setup_class(cls):
        device1 = Device("Server01", "Linux", "192.168.100.1", "root", "1234")
        device2 = Device("Server02", "Linux", "192.168.100.2", "root", "1234")
        device3 = Device("Switch01", "Cisco", "192.168.200.1", "admin", "1234")
        cls.testSuite.createDevice("Server01", "Linux", "192.168.100.1", "root", "1234")
        cls.testSuite.createDevice("Server02", "Linux", "192.168.100.2", "root", "1234")
        cls.testSuite.createDevice("Switch01", "Cisco", "192.168.200.1", "admin", "1234")
        cls.testSuite.createTest("testPingFromAToB", "ping", device1, "", "0")
        cls.testSuite.createTest("showNeighborsByArp", "arp", device2, "", "0")
        cls.testSuite.createTest("showNeighborsByCdp", "cdp", device3, "", "0")


    def test_getDeviceByName_First(self):
        assert self.testSuite.getDeviceByName("Server01") is not None
        assert self.testSuite.getDeviceByName("Server01").name == "Server01"
        assert self.testSuite.getDeviceByName("Server01").os == "Linux"
        assert self.testSuite.getDeviceByName("Server01").ipAddress == "192.168.100.1"
        assert self.testSuite.getDeviceByName("Server01").username == "root"
        assert self.testSuite.getDeviceByName("Server01").password == "1234"


    def test_getDeviceByName_NotFirst(self):
        assert self.testSuite.getDeviceByName("Server02") is not None
        assert self.testSuite.getDeviceByName("Server02").name == "Server02"
        assert self.testSuite.getDeviceByName("Server02").os == "Linux"
        assert self.testSuite.getDeviceByName("Server02").ipAddress == "192.168.100.2"
        assert self.testSuite.getDeviceByName("Server02").username == "root"
        assert self.testSuite.getDeviceByName("Server02").password == "1234"


    def test_getDeviceByName_Last(self):
        assert self.testSuite.getDeviceByName("Switch01") is not None
        assert self.testSuite.getDeviceByName("Switch01").name == "Switch01"
        assert self.testSuite.getDeviceByName("Switch01").os == "Cisco"
        assert self.testSuite.getDeviceByName("Switch01").ipAddress == "192.168.200.1"
        assert self.testSuite.getDeviceByName("Switch01").username == "admin"
        assert self.testSuite.getDeviceByName("Switch01").password == "1234"


    def test_getDeviceByName_NotFound(self):
        assert self.testSuite.getDeviceByName("no such device") is None


    def test_getTestByName_First(self):
        assert self.testSuite.getTestByName("testPingFromAToB") is not None
        assert self.testSuite.getTestByName("testPingFromAToB").name == "testPingFromAToB"
        assert self.testSuite.getTestByName("testPingFromAToB").command == "ping"


    def test_getTestByName_NotFirst(self):
        assert self.testSuite.getTestByName("showNeighborsByArp") is not None
        assert self.testSuite.getTestByName("showNeighborsByArp").name == "showNeighborsByArp"
        assert self.testSuite.getTestByName("showNeighborsByArp").command == "arp"

    def test_getTestByName_Last(self):
        assert self.testSuite.getTestByName("showNeighborsByCdp") is not None
        assert self.testSuite.getTestByName("showNeighborsByCdp").name == "showNeighborsByCdp"
        assert self.testSuite.getTestByName("showNeighborsByCdp").command == "cdp"

    def test_getTestByName_NotFound(self):
        assert self.testSuite.getTestByName("no such test") is None
