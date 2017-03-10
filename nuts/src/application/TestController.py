from src.data.TestSuite import TestSuite
from src.service.FileHandler import FileHandler
from src.service.Runner import Runner
from src.service.Evaluator import Evaluator
from src.service.salt_api_wrapper import SaltApi


class TestController:

    def __init__(self, test_file, max_iterations):
        self.test_suite = TestSuite("SuiteName")
        self.test_file = test_file
        self.file_handler = FileHandler(self.test_suite, self.test_file)
        self.runner = Runner(self.test_suite, SaltApi(), max_iterations=max_iterations)
        self.evaluator = Evaluator(self.test_suite)

    def logic(self):
        self.file_handler.read_file(self.test_file)
        self.run_tests()

    def run_tests(self):
        self.test_suite.print_all_test_cases()
        self.runner.run_all()
        self.evaluator.validate_all_results()
        if(self.test_suite.has_failed_tests()):
            if(self.check_re_run_failed_tests()):
                self.re_run_failed_tests()

    def re_run_failed_tests(self):
        self.test_suite.prepare_re_run()
        self.run_tests()

    def check_re_run_failed_tests(self):
        input_var = raw_input('Do you want to re-run the failed tests? \n' +
                              'Enter yes or y \n')
        return input_var.lower() == 'yes' or input_var.lower() == 'y'
