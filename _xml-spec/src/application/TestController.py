from src.data.TestSuite import TestSuite
from src.service.FileHandler import FileHandler
from src.service.Runner import Runner
from src.service.Evaluator import Evaluator

class TestController:

    testSuite = TestSuite("SuiteName")

    def __init__(self, testFile, devFile):
        self.testFile = testFile
        self.devFile = devFile
        self.fileHandler = FileHandler(self.testSuite, self.testFile, self.devFile)
        self.runner = Runner(self.testSuite)
        self.evaluator = Evaluator(self.testSuite)

    def logic(self):
        self.fileHandler.readFile(self.testFile, "tests")
        self.fileHandler.readFile(self.devFile, "devices")
        TestController.testSuite.printAllTestCases()
        TestController.testSuite.printAllDevices()

        self.runner.runAll()
        self.evaluator.printAllResults()