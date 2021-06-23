import pytest
from tests.utils import YAML_EXTENSION

from nuts.helpers.errors import NutsUnvalidatedResultError
from unittest.mock import Mock

from nornir.core.task import Result

from nuts.helpers.result import nuts_result_wrapper


def test_check_result(testdir):
    arguments = {
        "test_check_result": """
---
- test_module: tests.helpers.check_result
  test_class: TestCheckResult
  test_data:
    - kind: failed
    - kind: exception
    - kind: failed_exception
    - kind: ok
            """
    }
    testdir.makefile(YAML_EXTENSION, **arguments)

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
        wrapped.validate()
        assert wrapped.result == "Test"

    def test_accessing_unvalidated_result(self):
        res = nuts_result_wrapper(Result(host=None, failed=True), lambda x: "Test")
        with pytest.raises(NutsUnvalidatedResultError):
            res.result

    def test_returns_failed_result_on_transform_error(self):
        transform = Mock()
        thrown_exception = Exception("Test")
        transform.side_effect = [thrown_exception]
        wrapped = nuts_result_wrapper(Result(host=None, failed=False), transform)
        assert wrapped.failed
        assert wrapped.exception == thrown_exception
