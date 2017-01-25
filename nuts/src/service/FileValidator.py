import subprocess
import os
import sys
import logging


class FileValidator:
    def __init__(self, testFile):
        self.testFile = testFile
        self.logger = logging.getLogger('error_log')

    def validate(self):
        cur_dir = os.path.dirname(__file__)
        testfile = os.path.join(cur_dir, "testSchema.yaml")
        devfile = os.path.join(cur_dir, "deviceSchema.yaml")
        try:
            procTest = subprocess.Popen(['pykwalify -d ' + self.testFile + ' -s ' + testfile],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            print("Test-File: \n" + procTest.communicate()[0].decode('utf-8'))
        except Exception as e:
            print("Validator-Fehler")
            self.logger.exception("Validator-Fehler")
