from typing import Any, Optional, Callable

import pytest
from nornir.core.task import Result


class NutsResult:
    """
    Potentially holds the result or context information if any issues occurred
    """

    def __init__(
        self, result: Optional[Any] = None, failed: Optional[bool] = False, exception: Optional[BaseException] = None
    ):
        """
        Create a new NutsResult

        :param result: Result of the information gathering
        :param failed: Whether the information gathering failed or not
        :param exception: Exception which was thrown during the information gathering
        """
        self.result = result
        self.failed = failed
        self.exception = exception


@pytest.fixture
def check_result(single_result: NutsResult) -> None:
    """
    Ensure that the result has no exception and is not failed.
    Raises corresponding AssertionError based on the condition

    :param single_result: The result to be checked
    :return: None
    :raise AssertionError if single_result contains an exception or single_result is failed
    """
    assert not single_result.exception, "An exception was thrown during information gathering"
    assert not single_result.failed, "Information gathering failed"


def nuts_result_wrapper(nornir_result: Result, single_transform: Callable[[Result], Any]) -> NutsResult:
    """
    Wrap a nornir_result into a NutsResult

    :param nornir_result: The nornir_result which should be wrapped
    :param single_transform: Function that accepts the nornir_result and returns the desired information
    :return: NutsResult either containing the transformed result or context information
    """
    if nornir_result.failed:
        return NutsResult(failed=True, exception=nornir_result.exception)
    try:
        return NutsResult(single_transform(nornir_result))
    except Exception as exception:
        return NutsResult(failed=True, exception=exception)
