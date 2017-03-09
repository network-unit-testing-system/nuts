import datetime
import logging
from colorama import Fore


class Evaluator:
    def __init__(self, test_suite):
        self.test_suite = test_suite
        self.info_logger = logging.getLogger('info_log')

    def compare(self, test_case):
        if test_case.operator == "=":
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

    def _test_case_failed(self, test_case):
        return self.get_result(test_case) == 'ERROR'

    def validate_result(self, test_case):
        if self._test_case_failed(test_case):
            print(
                Fore.RED + test_case.name + ': Test error -------------------\n' +
                Fore.RESET + 'An error occurred while executing the test!')
            self.info_logger.warning(
                test_case.name + ': Test failed -------------------\nFailure while executing the test!')
            self.test_suite.mark_test_case_failed(test_case)
        elif self.compare(test_case):
            print(Fore.GREEN + test_case.name + ': Test passed -------------------------\n' +
                  Fore.RESET + 'Expected: ' + str(self.format_result(self.get_expected(test_case))) +
                  ' ' + test_case.operator + ' Actual: ' + self.format_result(str(self.get_result(test_case))))
            self.info_logger.warning('\n' + test_case.name + ': Test passed ------------------------- \nExpected: ' +
                                     str(self.get_expected(test_case)) + ' ' + test_case.operator +
                                     ' Actual:  ' + str(self.get_result(test_case)))
            self.test_suite.mark_test_case_passed(test_case)
        else:
            print(Fore.RED + test_case.name + ': Test failed -------------------\n' +
                  Fore.RESET + 'Expected: ' + str(self.get_expected(test_case)) + ' ' + test_case.operator +
                  ' Actual: ' + str(self.get_result(test_case)))
            self.info_logger.warning('\n' + test_case.name + ': Test failed ------------------- \nExpected: ' +
                                     str(self.get_expected(test_case)) + ' ' + test_case.operator +
                                     ' Actual:  ' + str(self.get_result(test_case)))
            self.test_suite.mark_test_case_failed(test_case)

    def validate_all_results(self):
        for test in self.test_suite.test_cases:
            self.validate_result(test)
        self.test_suite.print_statistics()
