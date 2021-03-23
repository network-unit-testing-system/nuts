"""Results of a network query."""

from typing import Any, Optional, Callable, TypeVar

from nornir.core.task import Result, MultiResult, AggregatedResult


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


T = TypeVar("T", Result, MultiResult, AggregatedResult)


def nuts_result_wrapper(nornir_result: T, single_transform: Callable[[T], Any]) -> NutsResult:
    """
    Wrap a nornir_result into a NutsResult

    :param nornir_result: The nornir_result which should be wrapped
    :param single_transform: Function that accepts the nornir_result and returns the desired information
    :return: NutsResult either containing the transformed result or context information
    """
    if nornir_result.failed:
        return NutsResult(failed=True, exception=nornir_result.exception)  # type: ignore[attr-defined]
    try:
        return NutsResult(single_transform(nornir_result))
    except Exception as exception:
        return NutsResult(failed=True, exception=exception)
