import pytest
from src.service.Evaluator import Evaluator
from src.data.TestSuite import TestSuite


class TestTestSuite:
    testSuite = TestSuite("TestTestSuite")
    eval = Evaluator(testSuite)

    @classmethod
    def setup_class(cls):
        cls.testSuite.createTest("testPingFromAToB", "connectivity", 'Server01', '8.8.8.8', "=", 'True')
        cls.testSuite.createTest("checkuser", "checkuser", 'Server02', '8.8.8.8', "=", 'admin')
        cls.testSuite.createTest("Count ospf neighbors", "countospfneighbors", 'Switch1', '', "=", '3')
        cls.eval = Evaluator(cls.testSuite)

    def test_compMultiple(self):
        list1 = []
        list2 = []
        list1.append('admin')
        list1.append('user')
        list2.append('user')
        list2.append('admin')
        self.eval.comp(list1, list2) is True

    def test_compMultipleFalse(self):
        list1 = []
        list2 = []
        list1.append('admin')
        list1.append('user')
        list2.append('user')
        self.eval.comp(list1, list2) is False

    def test_CompareSingleTrue(self):
        testCase = self.testSuite.getTestByName('Count ospf neighbors')
        result = {"resulttype": "single", "result": '3'}
        testCase.actualResult = result
        self.eval.compare(testCase) is 3

    def test_CompareSingleFalse(self):
        result = {"resulttype": "single", "result": 'False'}
        testCase = self.testSuite.getTestByName('testPingFromAToB')
        testCase.actualResult = result
        self.eval.compare(testCase) is False

    def test_CompareMultipleTrue(self):
        result = {"resulttype": "multiple", "result": ['admin', 'user']}
        testCase = self.testSuite.getTestByName('checkuser')
        testCase.actualResult = result
        self.eval.compare(testCase) is True

    def test_CompareMultipleFalse(self):
        result = {"resulttype": "multiple", "result": ['admin']}
        testCase = self.testSuite.getTestByName('checkuser')
        testCase.actualResult = result
        self.eval.compare(testCase) is False
