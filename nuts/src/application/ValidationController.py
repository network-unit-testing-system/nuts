from src.service.FileValidator import FileValidator


class ValidationController:
    fileHandler = None

    def __init__(self, testFile):
        self.testFile = testFile
        self.fileValidator = FileValidator(testFile)

    def logic(self):
        self.fileValidator.validate()
