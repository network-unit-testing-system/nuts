from .TestCase import TestCase
import logging


class TestSuite:
    name = ""
    testCases = []

    def __init__(self, name):
        TestSuite.name = name

    def createTest(self, name, command, devices, parameter, operator, expectedResult):
        test = TestCase(name, command, devices, parameter, operator, expectedResult)
        TestSuite.testCases.append(test)
        self.logger = logging.getLogger('error_log')

    def setActualResult(self, testCase, actualResult):
        self.getTestByName(testCase.name).setActualResult(actualResult)

    def getActualResult(self, testCase):
        return self.getTestByName(testCase.name).getActualResult()

    def getTestByName(self, name):
        for test in TestSuite.testCases:
            if test.name == name:
                return test

    def printAllTestCases(self):
        print("\nTestCases:")
        for test in TestSuite.testCases:
            print(test)

