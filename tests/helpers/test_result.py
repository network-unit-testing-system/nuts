import pytest

from nuts.context import NutsContext
from tests.utils import YAML_EXTENSION

from nuts.helpers.errors import NutsUnvalidatedResultError
from unittest.mock import Mock

from nornir.core.task import Result

from nuts.helpers.result import AbstractResultExtractor


def test_check_result(pytester):
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
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(errors=3, passed=1)


class MockResultExtractor(AbstractResultExtractor):
    single_transform = Mock()


@pytest.fixture
def extractor():
    return MockResultExtractor(NutsContext())


class TestNutsResultWrapper:
    def test_returns_failed_result_if_failed(self, extractor):
        wrapped = extractor.nuts_result_wrapper(Result(host=None, failed=True))
        assert wrapped.failed
        assert not extractor.single_transform.called

    def test_returns_transformed_result(self, extractor):
        extractor.single_transform.return_value = "Test"
        wrapped = extractor.nuts_result_wrapper(Result(host=None, failed=False))
        assert not wrapped.failed
        wrapped.validate()
        assert wrapped.result == "Test"

    def test_accessing_unvalidated_result(self, extractor):
        res = extractor.nuts_result_wrapper(Result(host=None, failed=True))
        with pytest.raises(NutsUnvalidatedResultError):
            res.result

    def test_returns_failed_result_on_transform_error(self, extractor):
        thrown_exception = Exception("Test")
        extractor.single_transform.side_effect = [thrown_exception]
        wrapped = extractor.nuts_result_wrapper(Result(host=None, failed=False))
        assert wrapped.failed
        assert wrapped.exception == thrown_exception
