import datetime
import logging


class Evaluator:
    def __init__(self, testSuite):
        self.testSuite = testSuite
        self.infologger = logging.getLogger('info_log')

    def compare(self, testCase):
        if testCase.operator == "=":
            print(testCase.actualResult["result"], testCase.expectedResult)
            return self.comp(testCase.actualResult["result"], testCase.expectedResult)
        elif testCase.operator == "<":
            return testCase.expectedResult < testCase.actualResult["result"]
        elif testCase.operator == ">":
            return testCase.expectedResult > testCase.actualResult["result"]
        elif testCase.operator == "not":
            return testCase.expectedResult != testCase.actualResult["result"]

    def getResult(self, testCase):
        return testCase.actualResult['result']
    
    def getExpected(self, testCase):
        return testCase.expectedResult

    def comp(self, list1, list2):
        if isinstance(list1,list) and isinstance(list1,list):
            return self.comp(set(list1), set(list2))
        else:
            return list1 == list2

    @staticmethod
    def formatResult(result):
        if isinstance(result,basestring):
            return result.encode('utf-8')
        if isinstance(result, list):
            return [x.encode('utf-8') for x in result]
        if isinstance(result,dict):
            return {x.encode('utf-8'):y.encode('utf-8') for x,y in result.items()}
        return str(result)
    
    def printResult(self, testCase):
        if self.getResult(testCase) == "ERROR":
            print(
                '\033[91m' + testCase.name + ": Test nicht bestanden -------------------\033[0m\nFehler bei der Ausfuehrung des Tests!")
            self.infologger.warning(
                testCase.name + ": Test nicht bestanden -------------------\nFehler bei der Ausfuehrung des Tests!")
        elif self.compare(testCase):
            print('\033[92m' + testCase.name + ": Test bestanden ------------------------- \033[0m\nExpected: " + str(
                self.formatResult(self.getExpected(testCase))) + " " + testCase.operator + " Actual: " + self.formatResult(str(self.getResult(testCase))))
            self.infologger.warning('\n' + testCase.name + ": Test bestanden ------------------------- \nExpected: " + str(
                self.getExpected(testCase)) + " " + testCase.operator + " Actual:  " + str(self.getResult(testCase)))
        else:
            print('\033[91m' + testCase.name + ": Test nicht bestanden -------------------\033[0m\nExpected: " + str(
                self.getExpected(testCase)) + " " + testCase.operator + " Actual: " + str(self.getResult(testCase)))
            self.infologger.warning('\n' + testCase.name + ": Test nicht bestanden ------------------- \nExpected: " + str(
                self.getExpected(testCase)) + " " + testCase.operator + " Actual:  " + str(self.getResult(testCase)))

    def printAllResults(self):
        for test in self.testSuite.testCases:
            self.printResult(test)
