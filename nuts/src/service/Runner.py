import json
import logging
from time import sleep


class Runner:
    def __init__(self, test_suite, salt_api, max_iterations=25, sleep_duration=0.1):
        self.test_suite = test_suite
        self.logger = logging.getLogger('error_log')
        self.info_logger = logging.getLogger('info_log')
        self.api = salt_api
        self.max_iterations = max_iterations
        self.sleep_duration = sleep_duration

    def run(self, test_case):
        result = self._get_task_result(test_case)
        self.test_suite.set_actual_result(test_case, result)

    def _collect_result(self, test_case):
        counter = 0
        not_contained = True
        while not_contained and (counter < self.max_iterations):
            salt_result = self.api.get_task_result(taskid=test_case.job_id)
            not_contained = False
            self.info_logger.debug('jid {} counter {} salt_result {}'.format(test_case.job_id, counter, salt_result))
            for minion in test_case.minions:
                if minion not in salt_result['return'][0]:
                    not_contained = True
                    sleep(self.sleep_duration)
            counter += 1
        return_value = self._extract_return(salt_result)
        self.test_suite.set_actual_result(test_case, return_value)

    def _start_task(self, test_case):
        try:
            task = self.create_task(test_case)
            self.api.connect()
            task_information = self.api.start_task_async(task)
            test_case.set_job(task_information)
            self.info_logger.debug(task_information)
        except Exception as e:
            self.logger.exception(e)

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
            self.info_logger.debug('{} returned {} '.format(test_case.name, result))
            if "ERROR" in result:
                raise Exception('A salt error occurred!\n' + result)
            return self._extract_return(result)
        except Exception as e:
            self.info_logger.exception('Error with {} \nSalt-Error: {} '.format(task, result))
            self.logger.exception("Error with {} \nSalt-Error: {} '\n'\n".format(task, result))
            self.logger.exception(e)
            return {
                'resulttype': 'single',
                'result': 'ERROR'
            }

    @staticmethod
    def _extract_return(result):
        '''This helper extracts the returnvalue from the result
        At the moment it only expects one return value for each task'''
        result_dict = result['return'][0]
        return {k: Runner._extract_result_entry(v) for k, v in result_dict.iteritems()}

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
            started_counter = 0
            for test in self.test_suite.test_cases:
                self.info_logger.info("Start test " + test.name)
                self._start_task(test)
                started_counter += 1
                self.info_logger.info("Started test {} of {}".format(started_counter, len(self.test_suite.test_cases)))
            test_counter = 0
            self.info_logger.info('----------------Started all tests-----------------')
            for test in self.test_suite.test_cases:
                self.info_logger.info("CollectResult of Test " + test.name)
                self._collect_result(test)
                test_counter += 1
                self.info_logger.info("Collected results from {} of {} tests"
                                      .format(test_counter, len(self.test_suite.test_cases)))
            self.info_logger.info('--------------Collected all results---------------')
        else:
            for test in self.test_suite.test_cases:
                self.info_logger.info("Start Test " + test.name)
                self.run(test)
            self.info_logger.info("\n")
