import subprocess
#import progressbar
import json
import logging
from time import sleep
from .salt_api_wrapper import SaltApi

class Runner:
    def __init__(self, testSuite):
        self.testSuite = testSuite
        self.logger = logging.getLogger('error_log')
        self.api = SaltApi()

    def run(self, testCase):
        self.api.connect()
        result = ''
        try:
            task = {
                'targets': self.testSuite.getDeviceDestination(testCase),
                'function': 'nuts.{}'.format(testCase.command),
                'arguments': testCase.parameter}
            result = self.api.start_task(task)
          
            if "ERROR" in result:
                raise Exception('A salt error occurred!\n' + result)
            self.testSuite.setActualResult(testCase, json.loads(self._extractReturn(result)))
        except Exception as e:
            self.testSuite.setActualResult(testCase, json.loads('{"resulttype": "single", "result": "ERROR"}'))
            print("Error with {} \nSalt-Error: {} '\n'\n".format(task,result))
            self.logger.exception("Error with {} \nSalt-Error: {} '\n'\n".format(task,result))
    def _extractReturn(self,result):
        '''This helper extracts the returnvalue from the result
        At the moment it only expects one return value for each task'''
        return result['return'][0].itervalues().next()

    def runAll(self):
        print("\n")
        for test in self.testSuite.testCases:
            print("Start Test " + test.name)
            self.run(test)
            print("\n")
