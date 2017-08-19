from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import os
from pykwalify.core import Core, SchemaError


class FileValidator(object):
    def __init__(self, test_file):
        self.test_file = test_file
        self.application_logger = logging.getLogger('nuts-application')
        self.validation_logger = logging.getLogger('nuts-validation')

    def validate(self):
        cur_dir = os.path.dirname(__file__)
        test_file = os.path.join(cur_dir, 'testSchema.yaml')
        try:
            c = Core(source_file=self.test_file, schema_files=[test_file])
            c.validate(raise_exception=True)
            return True
        except SchemaError as e:
            self.validation_logger.exception('Validation error')
            self.validation_logger.info(e.msg)
            self.application_logger.debug(e)
            return False
