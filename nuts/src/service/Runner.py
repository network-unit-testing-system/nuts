import subprocess
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
            result = self._get_task_result(testCase)
            self.testSuite.setActualResult(testCase, result)
    def _get_task_result(self, testCase):
        result = ''
        task = {
                'targets': testCase.devices,
                'function': 'nuts.{}'.format(testCase.command),
                'arguments': testCase.parameter}
        try:
            self.api.connect()
            result = self.api.start_task(task)
            print(result)
            if "ERROR" in result:
                raise Exception('A salt error occurred!\n' + result)
            extracted_result = self._extractReturn(result)
            if(extracted_result == None):
                return {
                    'resulttype':'single',
                    'result':None
                }
            return extracted_result
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
        return result['return'][0].itervalues().next()

    def runAll(self):
        print("\n")
        for test in self.testSuite.testCases:
            print("Start Test " + test.name)
            self.run(test)
            print("\n")
