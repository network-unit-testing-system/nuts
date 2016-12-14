import subprocess
import progressbar
import json
import logging
from time import sleep

class Runner:

    def __init__(self, testSuite):
        self.testSuite = testSuite
        self.logger = logging.getLogger('nuts_error_log')

    def run(self, testCase):
        bar = progressbar.ProgressBar(maxval=20, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        cmd = 'salt-call ' + "nuts." + testCase.command + " " + self.testSuite.getDeviceDestination(
            testCase) + " " + ' '.join(testCase.parameter) + " " + self.testSuite.getDeviceOS(
            testCase) + " " + self.testSuite.getUsername(testCase) + " " + self.testSuite.getPassword(testCase)
        result = ''
        try:
            proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

            for i in bar(range(100)):
                if proc.poll() == 0:
                    bar.update(100)
                    break
                elif proc.poll() == -1:

                    break
                else:
                    if i == 99:
                        if proc.poll() != 0:
                            sleep(0.2)
                    sleep(0.1)
                    bar.update(i)

            result = proc.communicate()[0].decode('utf-8')
            if "ERROR" in result:
                raise Exception('Ein Salt Error ist aufgetreten!\n' + result)

            self.testSuite.setActualResult(testCase, json.loads(result[result.index('{'):(result.index('}') + 1)]))
        except Exception as e:
            self.testSuite.setActualResult(testCase, json.loads('{"resulttype": "single", "result": "ERROR"}'))
            print("Runner-Fehler beim Befehl: " + cmd)
            self.logger.exception("Error beim Befehl: " + cmd + '\nSalt Error:' + result + '\n\n')

    def runAll(self):
        print("\n")
        for test in self.testSuite.testCases:
            print("Start Test " + test.name)
            self.run(test)
            print("\n")