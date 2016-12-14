import datetime
import logging

class Evaluator:

    def __init__(self, testSuite):
        self.testSuite = testSuite
        self.date = str(datetime.datetime.now())
        self.logger = logging.getLogger('nuts_info_log')


    def compare(self, testCase):
        if testCase.operator == "=":
            if testCase.actualResult["resulttype"] == "single":
                return testCase.expectedResult == testCase.actualResult["result"]
            elif testCase.actualResult["resulttype"] == "multiple":
                return self.comp(testCase.actualResult["result"], testCase.expectedResult)
        elif testCase.operator == "<":
            return testCase.expectedResult < testCase.actualResult["result"]
        elif testCase.operator == ">":
            return testCase.expectedResult > testCase.actualResult["result"]
        elif testCase.operator == "not":
            return testCase.expectedResult != testCase.actualResult["result"]

    def getResult(self, testCase):
        res = ''
        if testCase.actualResult["resulttype"] == "single":
            res = testCase.actualResult["result"]
        elif testCase.actualResult["resulttype"] == "multiple":
            res = ' '.join(testCase.actualResult["result"])
        return res

    def getExpected(self, testCase):
        exp = ''
        if testCase.actualResult["resulttype"] == "single":
            exp = testCase.expectedResult
        elif testCase.actualResult["resulttype"] == "multiple":
            exp = ' '.join(testCase.expectedResult)
        return exp

    def comp(self, list1, list2):
        if len(list1) != len(list2):
            return False
        for val in list1:
            if val not in list2:
                return False
        return True


    def printResult(self, testCase):
        if self.getResult(testCase) == "ERROR":
            print('\033[91m' + testCase.name + ": Test nicht bestanden -------------------\033[0m\nFehler bei der Ausführung des Tests!")
            self.logger.warning(testCase.name + ": Test nicht bestanden -------------------\nFehler bei der Ausführung des Tests!")
        elif self.compare(testCase):
            print('\033[92m' + testCase.name + ": Test bestanden ------------------------- \033[0m\nExpected: " + str(self.getExpected(testCase)) + " " + testCase.operator +  " Actual: " + str(self.getResult(testCase)))
            self.logger.warning('\n' + testCase.name + ": Test bestanden ------------------------- \nExpected: " + str(self.getExpected(testCase)) + " " + testCase.operator + " Actual:  " + str(self.getResult(testCase)))
        else:
            print('\033[91m' + testCase.name + ": Test nicht bestanden -------------------\033[0m\nExpected: " + str(self.getExpected(testCase)) + " " + testCase.operator + " Actual: " + str(self.getResult(testCase)))
            self.logger.warning('\n' + testCase.name + ": Test nicht bestanden ------------------- \nExpected: " + str(self.getExpected(testCase)) + " " + testCase.operator + " Actual:  " + str(self.getResult(testCase)))

    def printAllResults(self):
        for test in self.testSuite.testCases:
            self.printResult(test)