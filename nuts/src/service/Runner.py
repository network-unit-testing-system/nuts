#import progressbar
import json
import logging
from time import sleep

class Runner:
    def __init__(self, testSuite,salt_api):
        self.testSuite = testSuite
        self.logger = logging.getLogger('error_log')
        self.api = salt_api
        
    def run(self, testCase):
        self._start_task(testCase)
        
        #    result = self._get_task_result(testCase)
        #    self.testSuite.setActualResult(testCase, result)
    def collectResult(self, test_case):
        counter = 0
        not_contained = True
        while not_contained:
            xx = self.api.get_task_result(taskid=test_case.job_id)
            not_contained = False
            print("jid {} counter {} xx {}".format(test_case.job_id, counter, xx))
            for minion in test_case.minions:
                if not minion in xx['return'][0]:
                    not_contained = True
                    sleep(0.1)
                    counter += 1
        print(counter)
        return_value = self._extractReturn(xx)
        self.testSuite.setActualResult(test_case, return_value)
        
    def _start_task(self, test_case):
        try:
            task = self.create_task(test_case)
            self.api.connect()
            task_information = self.api.start_task_async(task)
            test_case.set_job(task_information)
            #xx = self.api.get_task_result(result)
            print(task_information)
            #print(xx)
        except Exception as e:
            print(e)

            
    @staticmethod
    def create_task(testCase):
        task = {
            'targets':testCase.devices, 
            'function':'nuts.{}'.format(testCase.command), 
            'arguments':testCase.parameter}
        return task

    def _get_task_result(self, testCase):
        result = ''
        task = self.create_task(testCase)
        try:
            self.api.connect()
            result = self.api.start_task(task)
            #result = self.api.start_task_async(task)
            #xx = self.api.get_task_result(result)
            print(result)
            #print(xx)
            if "ERROR" in result:
                raise Exception('A salt error occurred!\n' + result)
            return self._extractReturn(result)
        except Exception as e:
            print(e)
            print("Error with {} \nSalt-Error: {} '\n'\n".format(task,result))
            self.logger.exception("Error with {} \nSalt-Error: {} '\n'\n".format(task,result))
            return {
                'resulttype':'single',
                'result':'ERROR'
            }
           
        
    @staticmethod
    def _extractReturn(result):
        '''This helper extracts the returnvalue from the result
        At the moment it only expects one return value for each task'''
        extracted_result = result['return'][0].itervalues().next()
        if(extracted_result == None):
                return {
                    'resulttype':'single',
                    'result':None
                }
        return json.loads(extracted_result)

    def run_all(self):
        print("\n")
        started_counter = 0
        for test in self.testSuite.testCases:
            print("Start test " + test.name)
            self.run(test)
            started_counter += 1
            print("Started test {} of {}".format(started_counter, len(self.testSuite.testCases)))
            print("\n")
        test_counter = 0
        for test in self.testSuite.testCases:
            print("CollectResult of Test " + test.name)
            self.collectResult(test)
            test_counter += 1
            print("Collected results from {} of {} tests".format(test_counter, len(self.testSuite.testCases)))
            print("\n")
