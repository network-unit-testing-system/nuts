from .TestCase import TestCase
import logging


class TestSuite:
    name = ""
    test_cases = []

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

    def print_all_test_cases(self):
        print("\nTestCases:")
        for test in TestSuite.test_cases:
            print(test)
