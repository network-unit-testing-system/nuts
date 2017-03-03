import os
import sys
import logging
from pykwalify.core import Core

class FileValidator:
    def __init__(self, test_file):
        self.test_file = test_file
        self.logger = logging.getLogger('error_log')

    def validate(self):
        cur_dir = os.path.dirname(__file__)
        test_file = os.path.join(cur_dir, "testSchema.yaml")
        try:
            c = Core(source_file=self.test_file, schema_files=[test_file])
            c.validate(raise_exception=True)
            return True
        except Exception as e:
            print("Validator-Fehler")
            self.logger.exception("Validator-Fehler")
            return False