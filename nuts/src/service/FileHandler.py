import yaml
import logging


class FileHandler:
    def __init__(self, test_suite, test_file):
        self.test_suite = test_suite
        self.test_file = test_file
        self.logger = logging.getLogger('error_log')

    def yaml(self):
        return yaml.dump(self.__dict__)

    @staticmethod
    def add_tests(data, test_suite):
        values = yaml.safe_load(data)
        for val in values:
            test_suite.create_test(val["name"], val["command"], val["devices"], val["parameter"], val["operator"],
                                   val["expected"])

    def read_file(self, file):
        try:
            from yaml import CLoader as Loader, CDumper as Dumper
        except ImportError:
            from yaml import Loader, Dumper

        with open(file, 'r') as stream:
            try:
                self.add_tests(stream, self.test_suite)
            except yaml.YAMLError as exc:
                print("Import-failure while processing file: {}".format(file))
                self.logger.exception("Import-failure while processing file: {}".format(file))
