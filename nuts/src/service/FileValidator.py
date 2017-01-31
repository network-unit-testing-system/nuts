import subprocess
import os
import sys
import logging
from pykwalify.core import Core

class FileValidator:
    def __init__(self, testFile):
        self.testFile = testFile
        self.logger = logging.getLogger('error_log')

    def validate(self):
        cur_dir = os.path.dirname(__file__)
        testfile = os.path.join(cur_dir, "testSchema.yaml")
        try:
            c = Core(source_file=self.testFile, schema_files=[testfile])
            c.validate(raise_exception=True)
            return True
        except Exception as e:
            print("Validator-Fehler")
            self.logger.exception("Validator-Fehler")
            return False