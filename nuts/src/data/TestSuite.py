from .TestCase import TestCase
import logging
from colorama import Fore


class TestSuite:

    def __init__(self, name):
        self.name = name
        self.test_cases = []
        self.test_cases_failed = []
        self.test_cases_passed = []

    def create_test(self, name, command, devices, parameter, operator, expected_result):
        test = TestCase(name, command, devices, parameter, operator, expected_result)
        self.test_cases.append(test)
        self.logger = logging.getLogger('error_log')
        self.info_logger = logging.getLogger('info_log')

    def set_actual_result(self, test_case, actual_result):
        self.get_test_by_name(test_case.name).set_actual_result(actual_result)

    def get_actual_result(self, test_case):
        return self.get_test_by_name(test_case.name).get_actual_result()

    def get_test_by_name(self, name):
        for test in self.test_cases:
            if test.name == name:
                return test

    def mark_test_case_failed(self, test_case):
        self.test_cases_failed.append(test_case)

    def mark_test_case_passed(self, test_case):
        self.test_cases_passed.append(test_case)

    def has_failed_tests(self):
        return self.test_cases_failed

    def prepare_re_run(self):
        self.test_cases = self.test_cases_failed
        self.test_cases_failed = []

    def print_statistics(self):
        tests_passed = len(self.test_cases_passed)
        tests_failed = len(self.test_cases_failed)
        self.info_logger.info('---------------------Summary----------------------')
        self.info_logger.info(Fore.GREEN  + '{} out of {} tests passed'.format(tests_passed, tests_passed + tests_failed))
        if(tests_failed > 0):
            self.info_logger.info(Fore.RED + '{} out of {} tests failed'.format(tests_failed, tests_passed + tests_failed))

    def print_all_test_cases(self):
        self.info_logger.info('\nTestCases:')
        for test in self.test_cases:
            self.info_logger.info(test)
