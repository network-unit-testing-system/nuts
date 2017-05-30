class Evaluation(object):
    def __init__(self, expected_result, operator):
        self.evaluation_results = []
        self.expected_result = expected_result
        self.operator = operator

    def result(self):
        passed = True
        for result in self.evaluation_results:
            if not result.passed:
                passed = False
        return passed
