import pytest
from src.data.Evaluation import Evaluation
from src.data.EvaluationResult import EvaluationResult


@pytest.fixture
def example_evaluation():
    evaluation = Evaluation("expected_result", "=")
    evaluation.evaluation_results.append(EvaluationResult("minion", "actual_result", True))
    evaluation.evaluation_results.append(EvaluationResult("minion2", "actual_result", True))
    evaluation.evaluation_results.append(EvaluationResult("minion3", "actual_result", True))
    return evaluation


class TestEvaluation:

    def test_result_true(self, example_evaluation):
        assert example_evaluation.result() is True

    def test_first_result_false(self, example_evaluation):
        example_evaluation.evaluation_results[0].passed = False
        assert example_evaluation.result() is False

    def test_middle_result_false(self, example_evaluation):
        example_evaluation.evaluation_results[1].passed = False
        assert example_evaluation.result() is False

    def test_last_result_false(self, example_evaluation):
        example_evaluation.evaluation_results[-1].passed = False
        assert example_evaluation.result() is False

    def test_result_empty(self):
        evaluation = Evaluation("expected_result", "=")
        assert evaluation.result() is True
