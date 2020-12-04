from unittest.mock import Mock

from nornir.core.task import Result

from pytest_nuts.helpers.result import nuts_result_wrapper


def test_check_result(testdir):
    arguments = {
        "test_check_result": """
import pytest
from pytest_nuts.helpers.result import NutsResult

failed_result = NutsResult(failed=True)
exception_result = NutsResult(exception=Exception("TestException"))
failed_exception_result = NutsResult(failed=True, exception=Exception("TestException"))
ok_result = NutsResult("TestData")

class TestCheckResult:
    @pytest.mark.usefixtures("check_nuts_result")
    @pytest.mark.parametrize("single_result", [failed_result, exception_result, failed_exception_result, ok_result])
    def test_raises_error_if_exception(self):
        pass
            """
    }
    testdir.makepyfile(**arguments)

    result = testdir.runpytest()
    result.assert_outcomes(errors=3, passed=1)


class TestNutsResultWrapper:
    def test_returns_failed_result_if_failed(self):
        transform = Mock()
        wrapped = nuts_result_wrapper(Result(host=None, failed=True), transform)
        assert wrapped.failed
        assert not transform.called

    def test_returns_transformed_result(self):
        wrapped = nuts_result_wrapper(Result(host=None, failed=False), lambda x: "Test")
        assert not wrapped.failed
        assert wrapped.result == "Test"

    def test_returns_failed_result_on_transform_error(self):
        transform = Mock()
        thrown_exception = Exception("Test")
        transform.side_effect = [thrown_exception]
        wrapped = nuts_result_wrapper(Result(host=None, failed=False), transform)
        assert wrapped.failed
        assert wrapped.exception == thrown_exception
