from nuts.service.file_validator import FileValidator


class ValidationController(object):
    def __init__(self, test_file):
        self.test_file = test_file
        self.file_validator = FileValidator(test_file)

    def logic(self):
        return self.file_validator.validate()
