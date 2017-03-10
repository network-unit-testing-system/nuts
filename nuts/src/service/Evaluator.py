import datetime
import logging
from colorama import Fore
from src.data.EvaluationResult import EvaluationResult
from src.data.Evaluation import Evaluation


class Evaluator:
    def __init__(self, test_suite):
        self.test_suite = test_suite
        self.info_logger = logging.getLogger('info_log')

    def compare(self, test_case):
        evaluation = Evaluation(test_case.expected_result, test_case.operator)
        for minion in test_case.minions:
            evaluation.evaluation_results.append(self.compare_minion(test_case, minion))
        return evaluation

    def compare_minion(self, test_case, minion):
        actual_result = test_case.extract_actual_result()
        if(minion in actual_result):
            if test_case.operator == "=":
                compare = self.comp(test_case.expected_result, actual_result[minion])
            elif test_case.operator == "<":
                compare = test_case.expected_result < actual_result[minion]
            elif test_case.operator == ">":
                compare = test_case.expected_result > actual_result[minion]
            elif test_case.operator == "not":
                compare = test_case.expected_result != actual_result[minion]
        else:
            compare = False
        return EvaluationResult(minion, actual_result[minion], compare)

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
        return test_case.extract_actual_result() == 'ERROR'

    def validate_result(self, test_case):
        if self._test_case_failed(test_case):
            print(
                Fore.RED + test_case.name + ': Test error -------------------\n' +
                Fore.RESET + 'An error occurred while executing the test!')
            self.info_logger.warning(
                test_case.name + ': Test failed -------------------\nFailure while executing the test!')
            self.test_suite.mark_test_case_failed(test_case)
        elif self.compare(test_case).result():
            print(Fore.GREEN + test_case.name + ': Test passed -------------------------\n' +
                  Fore.RESET + 'Expected: ' + str(self.format_result(test_case.expected_result)) +
                  ' ' + test_case.operator + ' Actual: ' + self.format_result(str(test_case.extract_actual_result())))
            self.info_logger.warning('\n' + test_case.name + ': Test passed ------------------------- \nExpected: ' +
                                     str(test_case.expected_result) + ' ' + test_case.operator +
                                     ' Actual:  ' + str(test_case.extract_actual_result()))
            self.test_suite.mark_test_case_passed(test_case)
        else:
            print(Fore.RED + test_case.name + ': Test failed -------------------\n' +
                  Fore.RESET + 'Expected: ' + str(test_case.expected_result) + ' ' + test_case.operator +
                  ' Actual: ' + str(test_case.extract_actual_result()))
            self.info_logger.warning('\n' + test_case.name + ': Test failed ------------------- \nExpected: ' +
                                     str(test_case.expected_result) + ' ' + test_case.operator +
                                     ' Actual:  ' + str(test_case.extract_actual_result()))
            self.test_suite.mark_test_case_failed(test_case)

    def validate_all_results(self):
        for test in self.test_suite.test_cases:
            self.validate_result(test)
        self.test_suite.print_statistics()
