from src.data.TestSuite import TestSuite
from src.service.FileHandler import FileHandler
from src.service.Runner import Runner
from src.service.Evaluator import Evaluator
from src.service.salt_api_wrapper import SaltApi


class TestController:
    test_suite = TestSuite("SuiteName")

    def __init__(self, test_file):
        self.test_file = test_file
        self.file_handler = FileHandler(self.test_suite, self.test_file)
        self.runner = Runner(self.test_suite, SaltApi())
        self.evaluator = Evaluator(self.test_suite)

    def logic(self):
        self.file_handler.read_file(self.test_file)
        TestController.test_suite.print_all_test_cases()
        self.runner.run_all()
        self.evaluator.print_all_results()
