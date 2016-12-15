import subprocess
import os
import sys
import logging
class FileValidator:


    def __init__(self, testFile, deviceFile):
        self.testFile = testFile
        self.deviceFile = deviceFile
        self.logger = logging.getLogger('nuts_error_log')

    def validate(self):
        cur_dir = os.path.dirname(__file__)
        testfile = os.path.join(cur_dir, "testSchema.yaml")
        devfile = os.path.join(cur_dir, "deviceSchema.yaml")
        try:
            if self.deviceFile == "T":
                procTest = subprocess.Popen(['/opt/nuts/env/bin/pykwalify -d ' +  self.testFile + ' -s ' + testfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                print("Test-File: \n" + procTest.communicate()[0].decode('utf-8'))
            elif self.deviceFile == "D":
                procDev = subprocess.Popen(['/opt/nuts/env/bin/pykwalify -d ' +  self.deviceFile + ' -s ' + devfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                print("Device-File: \n" + procDev.communicate()[0].decode('utf-8'))
            else:
                procTest = subprocess.Popen(['/opt/nuts/env/bin/pykwalify -d ' +  self.testFile + ' -s ' + testfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                procDev = subprocess.Popen(['/opt/nuts/env/bin/pykwalify -d ' +  self.deviceFile + ' -s ' + devfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                print("Test-File: \n" + procTest.communicate()[0].decode('utf-8'))
                print("Device-File: \n" + procDev.communicate()[0].decode('utf-8'))
        except Exception as e:
            print("Validator-Fehler")
            self.logger.exception("Validator-Fehler")



