import logging

import yaml


class FileHandler(object):
    def __init__(self, test_suite, test_file):
        self.test_suite = test_suite
        self.test_file = test_file
        self.application_logger = logging.getLogger('nuts-application')
        self.test_report_logger = logging.getLogger('nuts-test-report')

    def yaml(self):
        return yaml.dump(self.__dict__)

    @staticmethod
    def add_tests(data, test_suite):
        values = yaml.safe_load(data)
        for val in values:
            test_suite.create_test(val['name'], val['command'], val['devices'], val['parameter'], val['operator'],
                                   val['expected'])

    def read_file(self, filename):
        try:
            from yaml import CLoader as Loader, CDumper as Dumper
        except ImportError:
            from yaml import Loader, Dumper

        with open(filename, 'r') as stream:
            try:
                self.add_tests(stream, self.test_suite)
            except yaml.YAMLError:
                self.application_logger.exception('Import-failure while processing file: %s', filename)
