from src.data.TestSuite import TestSuite
from src.service.FileHandler import FileHandler
from src.service.Runner import Runner
from src.service.Evaluator import Evaluator


class TestController:
    testSuite = TestSuite("SuiteName")

    def __init__(self, testFile):
        self.testFile = testFile
        self.fileHandler = FileHandler(self.testSuite, self.testFile)
        self.runner = Runner(self.testSuite)
        self.evaluator = Evaluator(self.testSuite)

    def logic(self):
        self.fileHandler.readFile(self.testFile)
        TestController.testSuite.printAllTestCases()

        self.runner.runAll()
        self.evaluator.printAllResults()
