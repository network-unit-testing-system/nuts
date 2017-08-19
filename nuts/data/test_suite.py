from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from colorama import Fore

from .test_case import TestCase


class TestSuite(object):
    def __init__(self, name):
        self.name = name
        self.test_cases_async = []
        self.test_cases_sync = []
        self.test_cases_failed = []
        self.test_cases_passed = []
        self.application_logger = logging.getLogger('nuts-application')
        self.test_report_logger = logging.getLogger('nuts-test-report')

    def create_test(self, **kwargs):
        async = kwargs.pop('async', None)
        test = TestCase(**kwargs)
        if async:
            self.test_cases_async.append(test)
        elif async is False:
            self.test_cases_sync.append(test)
        elif len(kwargs.get('setup', [])) or len(kwargs.get('teardown', [])):
            self.test_cases_sync.append(test)
        else:
            self.test_cases_async.append(test)

    def get_test_by_name(self, name):
        for test in self.test_cases_async + self.test_cases_sync:
            if test.name == name:
                return test

    def mark_test_case_failed(self, test_case):
        self.test_cases_failed.append(test_case)

    def mark_test_case_passed(self, test_case):
        self.test_cases_passed.append(test_case)

    def has_failed_tests(self):
        return self.test_cases_failed

    def prepare_re_run(self):
        self.test_report_logger.info('-------Rerun Failed Cases (only sync calls)-------')
        self.test_cases_sync = self.test_cases_failed
        self.test_cases_failed = []

    def print_statistics(self):
        tests_passed = len(self.test_cases_passed)
        tests_failed = len(self.test_cases_failed)
        self.test_report_logger.info('---------------------Summary----------------------')
        self.test_report_logger.info(Fore.GREEN + '%s out of %s tests passed', tests_passed,
                                     tests_passed + tests_failed)
        if tests_failed > 0:
            self.test_report_logger.info(Fore.RED + '%s out of %s tests failed', tests_failed,
                                         tests_passed + tests_failed)

    def print_all_test_cases(self):
        self.test_report_logger.info('\nTestCases:')
        if self.test_cases_async:
            self.test_report_logger.info('Async Tests:')
            for test in self.test_cases_async:
                self.test_report_logger.info(test)
        if self.test_cases_sync:
            self.test_report_logger.info('Sync Tests:')
            for test in self.test_cases_sync:
                self.test_report_logger.info(test)
