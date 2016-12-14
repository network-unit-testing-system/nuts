from src.service.FileValidator import FileValidator

class ValidationController:

    fileHandler = None

    def __init__(self, testFile, devFile):
        self.testFile = testFile
        self.devFile = devFile
        self.fileValidator = FileValidator(testFile, devFile)


    def logic(self):
       self.fileValidator.validate()
