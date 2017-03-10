import json
import logging
from time import sleep


class Runner:
    def __init__(self, test_suite, salt_api):
        self.test_suite = test_suite
        self.logger = logging.getLogger('error_log')
        self.api = salt_api

    def run(self, test_case):
        result = self._get_task_result(test_case)
        self.test_suite.set_actual_result(test_case, result)

    def _collect_result(self, test_case, max_iterations=10, sleep_duration=0.1):
        counter = 0
        not_contained = True
        while not_contained and (counter < max_iterations):
            xx = self.api.get_task_result(taskid=test_case.job_id)
            not_contained = False
            print("jid {} counter {} xx {}".format(test_case.job_id, counter, xx))
            for minion in test_case.minions:
                if minion not in xx['return'][0]:
                    not_contained = True
                    sleep(sleep_duration)
            counter += 1
        if not_contained:
            # TODO better solution for timeout
            timeout_result = {
                              'resulttype': 'single',
                              'result': 'TIMEOUT'
                              }
            self.test_suite.set_actual_result(test_case, timeout_result)
        else:
            return_value = self._extract_return(xx)
            self.test_suite.set_actual_result(test_case, return_value)

    def _start_task(self, test_case):
        try:
            task = self.create_task(test_case)
            self.api.connect()
            task_information = self.api.start_task_async(task)
            test_case.set_job(task_information)
            print(task_information)
        except Exception as e:
            print(e)

    @staticmethod
    def create_task(test_case):
        task = {
            'targets': test_case.devices,
            'function': 'nuts.{}'.format(test_case.command),
            'arguments': test_case.parameter
            }
        return task

    def _get_task_result(self, test_case):
        result = ''
        task = self.create_task(test_case)
        try:
            self.api.connect()
            result = self.api.start_task(task)
            print(result)
            if "ERROR" in result:
                raise Exception('A salt error occurred!\n' + result)
            return self._extract_return(result)
        except Exception as e:
            print(e)
            print("Error with {} \nSalt-Error: {} '\n'\n".format(task, result))
            self.logger.exception("Error with {} \nSalt-Error: {} '\n'\n".format(task, result))
            return {
                'resulttype': 'single',
                'result': 'ERROR'
            }

    @staticmethod
    def _extract_return(result):
        '''This helper extracts the returnvalue from the result
        At the moment it only expects one return value for each task'''
        result_dict = result['return'][0]
        result_dict = {k: Runner._extract_result_entry(v) for k, v in result_dict.iteritems()}
        if(len(result_dict) == 1):
            return result_dict.itervalues().next()
        else:
            return result_dict

    @staticmethod
    def _extract_result_entry(result_entry):
        if(result_entry is None):
                return {
                    'resulttype': 'single',
                    'result': None
                }
        else:
            return json.loads(result_entry)

    def run_all(self, execute_async=True):
        if execute_async:
            print("\n")
            started_counter = 0
            for test in self.test_suite.test_cases:
                print("Start test " + test.name)
                self._start_task(test)
                started_counter += 1
                print("Started test {} of {}".format(started_counter, len(self.test_suite.test_cases)))
                print("\n")
            test_counter = 0
            for test in self.test_suite.test_cases:
                print("CollectResult of Test " + test.name)
                self._collect_result(test)
                test_counter += 1
                print("Collected results from {} of {} tests".format(test_counter, len(self.test_suite.test_cases)))
                print("\n")
        else:
            for test in self.test_suite.test_cases:
                print("Start Test " + test.name)
                self.run(test)
                print("\n")
            print("\n")
