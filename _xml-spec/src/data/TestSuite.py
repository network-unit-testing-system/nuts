from .Device import Device
from .TestCase import TestCase
import logging
class TestSuite:
    name = ""
    testCases = []
    devices = []

    def __init__(self, name):
        TestSuite.name = name

    def createTest(self, name, command, devices, parameter, operator, expectedResult):
        test = TestCase(name, command, devices, parameter,operator, expectedResult)
        TestSuite.testCases.append(test)
        self.logger = logging.getLogger('nuts_error_log')


    def createDevice(self, name, os, destination, username, password):
        dev = Device(name, os, destination, username, password)
        TestSuite.devices.append(dev)

    def getDeviceOS(self, testCase):
        return self.getDeviceByName(testCase.devices).os

    def getUsername(self, testCase):
        return self.getDeviceByName(testCase.devices).username

    def getPassword(self, testCase):
        return self.getDeviceByName(testCase.devices).password

    def getDeviceDestination(self, testCase):
        return self.getDeviceByName(testCase.devices).destination

    def setActualResult(self, testCase, actualResult):
       self.getTestByName(testCase.name).setActualResult(actualResult)

    def getActualResult(self, testCase):
        return self.getTestByName(testCase.name).getActualResult()

    def getTestByName(self,name):
        for test in TestSuite.testCases:
            if test.name == name:
                return test

    def getDeviceByName(self,name):
        for dev in TestSuite.devices:
            if dev.name == name:
                return dev
        print("Der Device: \"{0}\" ist fehlerhaft oder fehlt im Device-File!\n".format(name))
        self.logger.error("Der Device: \"{0}\" ist fehlerhaft oder fehlt im Device-File!\n".format(name))
        return None

    def printAllTestCases(self):
        print("\nTestCases:")
        for test in TestSuite.testCases:
           print(test)

    def printAllDevices(self):
        print("\nDevices:")
        for dev in TestSuite.devices:
            print(dev)