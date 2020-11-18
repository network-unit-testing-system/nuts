from typing import Any, Optional

import pytest


class NutsResult:
    def __init__(
        self, result: Optional[Any] = None, failed: Optional[bool] = False, exception: Optional[BaseException] = None
    ):
        self.result = result
        self.failed = failed
        self.exception = exception

    def exception_or_failed(self):
        return self.exception or self.failed


@pytest.fixture
def check_result(single_result):
    assert not single_result.exception_or_failed(), "Task failed or an exception was thrown."
    yield


def nuts_result_wrapper(nornir_result, single_transform):
    if nornir_result.failed:
        return NutsResult(failed=True, exception=nornir_result.exception)
    try:
        return NutsResult(single_transform(nornir_result))
    except Exception as exception:
        return NutsResult(failed=True, exception=exception)
