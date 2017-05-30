from nuts.data.test_suite import TestSuite
from nuts.service.evaluator import Evaluator
from nuts.service.file_handler import FileHandler
from nuts.service.runner import Runner
from nuts.service.salt_api_wrapper import SaltApi
from nuts.service.settings import settings


class TestController(object):
    def __init__(self, test_file, max_iterations=None, max_retries=None):
        self.test_file = test_file
        if max_iterations:
            self.retries = max_iterations
        else:
            self.max_iterations = settings.get_variable('NUTS_WAIT_ITERATIONS', default=25)
        if max_iterations:
            self.retries = max_retries
        else:
            self.retries = settings.get_variable('NUTS_MAX_RETRIES', default=0)

        self.test_suite = TestSuite('SuiteName')
        self.file_handler = FileHandler(self.test_suite, self.test_file)
        self.runner = Runner(self.test_suite, SaltApi(), max_iterations=self.max_iterations)
        self.evaluator = Evaluator(self.test_suite)

    def logic(self):
        self.file_handler.read_file(self.test_file)
        self.run_tests()

    def run_tests(self):
        self.test_suite.print_all_test_cases()
        self.runner.run_all()
        self.evaluator.validate_all_results()
        while self.test_suite.has_failed_tests() and self.retries > 0:
            self.re_run_failed_tests()

    def re_run_failed_tests(self):
        self.test_suite.prepare_re_run()
        self.run_tests()
