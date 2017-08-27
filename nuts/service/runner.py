from __future__ import absolute_import
from __future__ import unicode_literals

import concurrent.futures
import logging
from time import sleep

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

from jinja2 import Template


class Runner(object):
    def __init__(self, test_suite, salt_api, max_iterations=25, sleep_duration=0.1):
        self.test_suite = test_suite
        self.application_logger = logging.getLogger('nuts-application')
        self.test_report_logger = logging.getLogger('nuts-test-report')
        self.api = salt_api
        self.max_iterations = max_iterations
        self.sleep_duration = sleep_duration

    def _collect_result(self, test_case):
        counter = 0
        not_contained = True
        while not_contained and (counter < self.max_iterations):
            salt_result = self.api.get_task_result(taskid=test_case.job_id)
            not_contained = False
            self.application_logger.debug('jid %s counter %s salt_result %s', test_case.job_id, counter, salt_result)
            for minion in test_case.minions:
                if minion not in salt_result['return'][0]:
                    not_contained = True
                    sleep(self.sleep_duration)
            counter += 1
        return_value = self._extract_return(salt_result)
        test_case.set_actual_result(return_value)
        if hasattr(test_case, 'teardown_tasks'):
            self.test_report_logger.debug('%s has %d teardown tasks', test_case.name, len(test_case.teardown_tasks))
            self._start_tasks(test_case.teardown_tasks, test_case.saved_data)

    def _start_test_async(self, test_case):
        try:
            saved_data = {}
            if hasattr(test_case, 'setup_tasks'):
                self.test_report_logger.debug('%s has %d setup tasks', test_case.name, len(test_case.setup_tasks))
                saved_data = self._start_tasks(test_case.setup_tasks)
                test_case.saved_data = saved_data
            task = self.create_test_task(test_case.devices, test_case.command, test_case.parameter, saved_data)
            task_information = self.api.start_task_async(task)
            test_case.set_job(task_information['return'][0]['jid'])
            test_case.set_minions(task_information['return'][0]['minions'])
            self.application_logger.debug(task_information)
            return True
        except URLError as e:
            self.application_logger.exception('Failed to start test case. Salt API URLError: %s', e.args[0].strerror)
            self.test_report_logger.debug(e)
            return False
        except KeyError as e:
            self.application_logger.exception('Failed to start test case. Probably devices match no minions')
            self.test_report_logger.debug(e)
            return False
        except Exception as e:
            self.application_logger.exception('Failed to start test case. Exception: %s', e.message)
            self.test_report_logger.debug(e)
            return False

    def _start_test_sync(self, test_case):
        if hasattr(test_case, 'setup_tasks'):
            self.test_report_logger.debug('%s has %d setup tasks', test_case.name, len(test_case.setup_tasks))
            saved_data = self._start_tasks(test_case.setup_tasks)
            test_case.saved_data = saved_data
        self.test_report_logger.debug('%s start sync test', test_case.name)
        result = self._get_task_result(test_case, saved_data)
        test_case.set_minions(result.keys())
        test_case.set_actual_result(result)
        if hasattr(test_case, 'teardown_tasks'):
            self.test_report_logger.debug('%s has %d teardown tasks', test_case.name, len(test_case.teardown_tasks))
            self._start_tasks(test_case.teardown_tasks, saved_data)

    def _start_tasks(self, tasks, result=None):
        if result is None:
            result = {}
        for task in tasks:
            save = task.pop('save', None)
            parameter = self.create_test_task(render_data=result, **task)
            response = self.api.start_task(parameter)
            self.test_report_logger.debug('%s %s returned %s', parameter['function'], parameter['arguments'], response)
            if not len(response['return'][0]):
                raise Exception('No device responding. devices: {}, command: {}'.format(task['devices'],
                                                                                        task['command']))
            for minion, value in response['return'][0].items():
                if value is None:
                    raise Exception('No response value from minion {}'.format(minion))
                elif 'is not available' in value:
                    raise Exception('Command {} not available on {}'.format(task['command'], minion))
                elif 'Passed invalid arguments' in value:
                    raise Exception('Passed invalid arguments for {} on {}. Arguments: {}'.format(task['command'],
                                                                                                  minion,
                                                                                                  task['parameter']))
            if save:
                # Normally no one minion will answer to a saved task. In this case the value is directly saved
                # in a dictionary. On multiple answers, the minion will be the dictionary key to access the value.
                # Multiple answer example for `save: ip`: `result['ip']['minion_name']`
                # One answer example for `save: ip`: `result['ip']`
                # The test write has to know when more then one minion will response.
                try:
                    if len(response['return'][0]) == 1:
                        result[save] = response['return'][0].popitem()[1]
                    elif len(response['return'][0]) > 1:
                        result[save] = response['return'][0]
                except KeyError:
                    pass

        return result

    @staticmethod
    def create_test_task(devices, command, parameter=None, render_data=None):
        if parameter is None:
            parameter = []
        if render_data is None:
            render_data = {}
        devices = Template(devices).render(render_data)
        command = Template(command).render(render_data)
        parameter = list(map(lambda x: Template(x).render(render_data), parameter))

        if '.' not in command:
            command = 'nuts.{}'.format(command)

        task = {
            'targets': devices,
            'function': command,
            'arguments': parameter
        }
        return task

    def _get_task_result(self, test_case, saved_data):
        result = ''
        task = self.create_test_task(test_case.devices, test_case.command, test_case.parameter, saved_data)
        try:
            result = self.api.start_task(task)
            self.application_logger.debug('%s returned %s ', test_case.name, result)
            if 'ERROR' in result:
                raise Exception('A salt error occurred!\n' + result)
            return self._extract_return(result)
        except Exception as e:
            self.application_logger.exception('Error with %s \nSalt-Error: %s ', task, result)
            self.test_report_logger.exception(e)
            return {
                'resulttype': 'single',
                'result': 'ERROR'
            }

    @staticmethod
    def _extract_return(result):
        '''This helper extracts the returnvalue from the result
        At the moment it only expects one return value for each task'''
        result_dict = result['return'][0]
        return {k: Runner._extract_result_entry(v) for k, v in result_dict.items()}

    @staticmethod
    def _extract_result_entry(result_entry):
        if result_entry is None:
            return {
                'resulttype': 'single',
                'result': None
            }
        else:
            return result_entry

    def run_all(self):
        try:
            self.api.connect()
        except URLError as e:
            self.application_logger.exception('Failed to connect to the server. Salt API URLError: %s',
                                              e.args[0].strerror)
            self.test_report_logger.debug(e)
            exit(1)
        # Run async tests
        started_counter = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for test in self.test_suite.test_cases_async:
                self.application_logger.info('Start test ' + test.name)
                futures.append(executor.submit(self._start_test_async, test))
            for x in concurrent.futures.as_completed(futures):
                if not x.result():
                    self.application_logger.error('Error starting async test')
                    executor.shutdown(wait=False)
                    exit(1)
                started_counter += 1
                self.application_logger.info('Started test %s of %s', started_counter,
                                             len(self.test_suite.test_cases_async))
        test_counter = 0
        self.application_logger.info('----------------Started all tests-----------------')
        for test in self.test_suite.test_cases_async:
            self.application_logger.info('CollectResult of Test ' + test.name)
            self._collect_result(test)
            test_counter += 1
            self.application_logger.info('Collected results from %s of %s tests', test_counter,
                                         len(self.test_suite.test_cases_async))
        self.application_logger.info('--------------Collected all results---------------')

        # Run sync tests
        for test in self.test_suite.test_cases_sync:
            self.application_logger.info('Start Test ' + test.name)
            self._start_test_sync(test)
        self.application_logger.info('\n')
