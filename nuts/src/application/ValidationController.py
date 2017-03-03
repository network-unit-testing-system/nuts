from src.service.FileValidator import FileValidator


class ValidationController:
    file_handler = None

    def __init__(self, test_file):
        self.test_file = test_file
        self.file_validator = FileValidator(test_file)

    def logic(self):
        return self.file_validator.validate()
