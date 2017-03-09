import datetime
import logging


class Evaluator:
    def __init__(self, test_suite):
        self.test_suite = test_suite
        self.info_logger = logging.getLogger('info_log')

    def compare(self, test_case):
        if test_case.operator == "=":
            print(test_case.actual_result["result"], test_case.expected_result)
            return self.comp(test_case.actual_result["result"], test_case.expected_result)
        elif test_case.operator == "<":
            return test_case.expected_result < test_case.actual_result["result"]
        elif test_case.operator == ">":
            return test_case.expected_result > test_case.actual_result["result"]
        elif test_case.operator == "not":
            return test_case.expected_result != test_case.actual_result["result"]

    def get_result(self, test_case):
        return test_case.actual_result['result']

    def get_expected(self, test_case):
        return test_case.expected_result

    def comp(self, list1, list2):
        if isinstance(list1, list) and isinstance(list1, list):
            return self.comp(set(list1), set(list2))
        else:
            return list1 == list2

    @staticmethod
    def format_result(result):
        if isinstance(result, basestring):
            return result.encode('utf-8')
        if isinstance(result, list):
            return [x.encode('utf-8') for x in result]
        if isinstance(result, dict):
            return {x.encode('utf-8'): y.encode('utf-8') for x, y in result.items()}
        return str(result)

    def print_result(self, test_case):
        if self.get_result(test_case) == "ERROR":
            print(
                '\033[91m' + test_case.name + ": Test error -------------------\033[0m\An error occurred while executing the test!")
            self.info_logger.warning(
                test_case.name + ": Test failed -------------------\033[0m\nFailure while executing the test!")
        elif self.compare(test_case):
            print('\033[92m' + test_case.name + ": Test passed ------------------------- \033[0m\nExpected: " + str(
                self.format_result(self.get_expected(test_case))) + " " + test_case.operator + " Actual: " + self.format_result(str(self.get_result(test_case))))
            self.info_logger.warning('\n' + test_case.name + ": Test passed ------------------------- \nExpected: " + str(
                self.get_expected(test_case)) + " " + test_case.operator + " Actual:  " + str(self.get_result(test_case)))
        else:
            print('\033[91m' + test_case.name + ": Test failed -------------------\033[0m\nExpected: " + str(
                self.get_expected(test_case)) + " " + test_case.operator + " Actual: " + str(self.get_result(test_case)))
            self.info_logger.warning('\n' + test_case.name + ": Test failed ------------------- \nExpected: " + str(
                self.get_expected(test_case)) + " " + test_case.operator + " Actual:  " + str(self.get_result(test_case)))

    def print_all_results(self):
        for test in self.test_suite.test_cases:
            self.print_result(test)
