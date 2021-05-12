"""Results of a network query."""

from typing import Any, Optional, Callable, TypeVar, Dict

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


def map_host_to_nutsresult(
    general_result: AggregatedResult, single_transform: Callable[[MultiResult], Any]
) -> Dict[str, NutsResult]:
    """
    Maps a host's name to its corresponding result, which in turn is
    wrapped into a NutsResult.

    Used when a nornir tasks queries properties of a host.

    :param general_result: The raw result as provided by nornir's executed task
    :param single_transform: function to be applied to a nornir MultiResult
    :return: Host mapped to a NutsResult
    """
    return {host: nuts_result_wrapper(multiresult, single_transform) for host, multiresult in general_result.items()}


def map_host_to_dest_to_nutsresult(
    general_result: AggregatedResult, single_transform: Callable[[Result], Any]
) -> Dict[str, Dict[str, NutsResult]]:
    """
    Maps a host's name to its corresponding destination and calls a helper function to further map
    that destination to a NutsResult.

    Used when a nornir task queries a host-destination pair.

    :param general_result: The raw result as provided by nornir's executed task
    :param single_transform: function to be applied to a nornir Result
    :return: The host mapped to its corresponding destination mapped to its NutsResult
    """
    return {
        host: map_dest_to_nutsresult(task_results, single_transform) for host, task_results in general_result.items()
    }


def map_dest_to_nutsresult(
    task_results: MultiResult, single_transform: Callable[[Result], Any]
) -> Dict[str, NutsResult]:
    """
    Maps a destination to the result of a nornir task which both belong to a host.

    Note 1: The nornir Result object does not contain a destination property, which often means that
    if the specific task fails (e.g. a ping fails), the destination information is missing in the result,
    and we do not know which destination actually failed.
    It is therefore necessary to patch the destination onto the Result object to later know which
    host-destination pair actually failed.
    As a consequence, typing must ignore the patched attribute.

    Note 2: Why the first result is not used and task_results[1:] instead:
    Tasks per host (such as pinging a series of destinations) are nornir (sub)tasks that are executed
    from within another task.
    For the main task to finish properly, we must return a single Result, such as
    `Result(host=task.host, result="All pings executed")`, that confirms the fulfillment of the subtasks.
    All subsequent Result objects are then the completed subtasks. We do not need the first Result that simply
    confirms the fulfilled subtasks, therefore we skip it explicitly and return `task_results[1:]`.

    :param task_results: The results of the nornir task per host
    :param single_transform: function to be applied to a single nornir Result
    :return: The destination mapped to the desired information
    """
    return {
        single_result.destination: nuts_result_wrapper(single_result, single_transform)  # type: ignore[attr-defined]
        for single_result in task_results[1:]
    }


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
