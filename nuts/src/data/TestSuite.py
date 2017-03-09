from .TestCase import TestCase
import logging


class TestSuite:
    name = ""
    test_cases = []
    test_cases_failed = []
    test_cases_passed = []

    def __init__(self, name):
        TestSuite.name = name

    def create_test(self, name, command, devices, parameter, operator, expected_result):
        test = TestCase(name, command, devices, parameter, operator, expected_result)
        TestSuite.test_cases.append(test)
        self.logger = logging.getLogger('error_log')

    def set_actual_result(self, test_case, actual_result):
        self.get_test_by_name(test_case.name).set_actual_result(actual_result)

    def get_actual_result(self, test_case):
        return self.get_test_by_name(test_case.name).get_actual_result()

    def get_test_by_name(self, name):
        for test in TestSuite.test_cases:
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
        print('\n {0} out of {2} passed\n {1} out of {2} failed\n'.format(len(self.test_cases_passed), len(self.test_cases_failed), len(self.test_cases_failed) + len(self.test_cases_passed)))

    def print_all_test_cases(self):
        print("\nTestCases:")
        for test in TestSuite.test_cases:
            print(test)
