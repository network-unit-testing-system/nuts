import yaml
import logging


class FileHandler:
    def __init__(self, testSuite, testFile):
        self.testSuite = testSuite
        self.testFile = testFile
        self.logger = logging.getLogger('error_log')

    def yaml(self):
        return yaml.dump(self.__dict__)

    @staticmethod
    def addTests(data, testSuite):
        values = yaml.safe_load(data)
        for val in values:
            testSuite.createTest(val["name"], val["command"], val["devices"], val["parameter"], val["operator"],
                                 val["expected"])

    def readFile(self, file):
        try:
            from yaml import CLoader as Loader, CDumper as Dumper
        except ImportError:
            from yaml import Loader, Dumper

        with open(file, 'r') as stream:
            try:
                self.addTests(stream, self.testSuite)
            except yaml.YAMLError as exc:
                print("Import-failure while processing file: {}".format(file))
                self.logger.exception("Import-failure while processing file: {}".format(file))
