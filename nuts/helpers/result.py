"""Results of a network query."""

import traceback
from typing import Any, Optional, TYPE_CHECKING, Dict

from nornir.core.task import MultiResult, AggregatedResult
from nuts.helpers.errors import NutsNornirError, NutsUnvalidatedResultError

if TYPE_CHECKING:
    from nuts.context import NutsContext


_TransformedResult = Dict[str, Any]


class NutsResult:
    """
    Potentially holds the result or context information if any issues occurred
    """

    def __init__(
        self,
        result: Optional[Any] = None,
        failed: Optional[bool] = False,
        exception: Optional[BaseException] = None,
    ) -> None:
        """
        Create a new NutsResult

        :param result: Result of the information gathering
        :param failed: Whether the information gathering failed or not
        :param exception: Exception which was thrown during the information gathering
        """
        self._result = result
        self.failed = failed
        self.exception = exception
        self._validated = False

    def validate(self) -> None:
        """Make sure the underlying result is a valid (i.e. non-failed) one."""
        if self.exception:
            header = "".join(
                traceback.format_exception_only(type(self.exception), self.exception)
            )
            raise NutsNornirError(
                f"An exception has occurred while executing nornir:\n"
                f"{header}\n"
                f"{self._result}"
            )
        if self.failed:
            raise NutsNornirError(f"Nornir execution has failed:\n" f"{self._result}")

        self._validated = True

    @property
    def result(self) -> Any:
        if not self._validated:
            raise NutsUnvalidatedResultError(
                f"Trying to access unvalidated result {self}"
            )
        return self._result


class AbstractResultExtractor:
    """Processes the general result that contains the raw overall results
    from the network query (mostly a nornir task)
    so that it can be passed on to the test class.

    Additionally wraps all the results that belong to one host into a
    NutsResult. There are two ways how this wrapping happens:

    1. Properties of a host are tested: One host maps to a NutsResult that contains
       all the queried properties.
    2. Properties of a connection between two hosts are tested: One host maps to a
       destination which maps to a NutsResult that contains all queried properties.
    """

    def __init__(self, context: "NutsContext") -> None:
        self._cached_result: Optional[_TransformedResult] = None
        self._nuts_ctx = context

    def single_transform(self, result: Any) -> Any:
        """
        Transforms a single (raw) result that belongs to a host from the overall
        general result set into the form that is required for the test class.
        :param result: raw data to be transformed
        :return: newly structured data
        """
        raise NotImplementedError

    def _map_host_to_nutsresult(
        self, general_result: AggregatedResult
    ) -> Dict[str, NutsResult]:
        """
        Maps a host's name to its corresponding result, which in turn is
        wrapped into a NutsResult.
        Used when a nornir tasks queries properties of a host.

        :param general_result: The raw result
                as provided by nornir's executed task
        :return: Host mapped to a NutsResult
        """
        return {
            host: self.nuts_result_wrapper(multiresult)
            for host, multiresult in general_result.items()
        }

    def _map_host_to_dest_to_nutsresult(
        self,
        general_result: AggregatedResult,
    ) -> Dict[str, Dict[str, NutsResult]]:
        """
        Maps a host's name to its corresponding destination and calls a helper function
        to further map that destination to a NutsResult.

        Used when a host-destination pair is tested.

        :param general_result: The raw result as provided by nornir's executed task
        :return: The host mapped to its corresponding destination
                  mapped to its NutsResult
        """
        return {
            host: self._map_dest_to_nutsresult(task_results)
            for host, task_results in general_result.items()
        }

    def _map_dest_to_nutsresult(
        self,
        task_results: MultiResult,
    ) -> Dict[str, NutsResult]:
        """
        Maps a destination to the result of a nornir task which both belong to a host.

        Note 1: The nornir Result object does not contain a destination property,
        which often means that if the specific task fails (e.g. a ping fails),
        the destination information is missing in the result, and we do not know
        which destination actually failed. It is therefore necessary to patch
        the destination onto the Result object to later know which host-destination pair
        actually failed. As a consequence, typing must ignore the patched attribute.

        Note 2: Why the first result is not used and task_results[1:] instead:
        Tasks per host (such as pinging a series of destinations) are
        nornir (sub)tasks that are executed from within another task.
        For the main task to finish properly, we must return a single Result, such as
        `Result(host=task.host, result="All pings executed")`, that confirms the
        fulfillment of the subtasks. All subsequent Result objects are then the
        completed subtasks. We do not need the first Result that simply confirms
        the fulfilled subtasks, therefore we skip it explicitly
        and return `task_results[1:]`.

        :param task_results: The results of the nornir task per host
        :return: The destination mapped to the desired information
        """
        return {
            single_result.destination: self.nuts_result_wrapper(  # type: ignore[attr-defined]  # noqa: E501
                single_result
            )
            for single_result in task_results[1:]
        }

    def nuts_result_wrapper(self, nornir_result: Any) -> NutsResult:
        """
        Wrap a nornir_result into a NutsResult

        :param nornir_result: The nornir_result which should be wrapped
        :return: NutsResult either containing the transformed result or
                 information if the network query has failed or thrown an exception.
        """
        if nornir_result.failed:
            return NutsResult(failed=True, exception=nornir_result.exception)
        try:

            return NutsResult(self.single_transform(nornir_result))
        except Exception as exception:
            tb = traceback.format_exc()
            return NutsResult(failed=True, exception=exception, result=tb)

    def transform_result(self, general_result: Any) -> _TransformedResult:
        """
        In most cases:
        1. calls map_host_to_nutsresult in case a host's properties are tested
        2. calls map_host_to_dest_to_nutsresult in case a host-destination pair's
           properties are tested.
        :param general_result: raw result
        :return: processed result ready to be passed to a test
        """
        raise NotImplementedError

    @property
    def transformed_result(self) -> _TransformedResult:
        """
        The (processed) results of the network task, ready to be passed on to a test's
        fixture. The results are cached, so that general_result does not need
        to be called multiple times as it might access the network.
        """
        if self._cached_result is None:
            self._cached_result = self.transform_result(self._nuts_ctx.general_result())
        return self._cached_result

    def single_result(self, nuts_test_entry: Dict[str, Any]) -> NutsResult:
        """The single result that belongs to one host.
        Must be overwritten in the case a host-destination pair is tested
        or the keyword that accesses nuts_test_entry differs.

        :param nuts_test_entry: a single entry in test_data
               of the test-bundle (the yaml-file)
        :return NutsResult of a host
        """
        host = nuts_test_entry["host"]
        assert (
            host in self.transformed_result
        ), f"Host {host} not found in aggregated result."
        return self.transformed_result[host]


class AbstractHostResultExtractor(AbstractResultExtractor):
    def transform_result(
        self, general_result: AggregatedResult
    ) -> Dict[str, NutsResult]:
        return self._map_host_to_nutsresult(general_result)

    def _simple_extract(self, single_result: MultiResult) -> Dict[Any, Any]:
        assert single_result[0].result is not None
        return single_result[0].result


class AbstractHostDestResultExtractor(AbstractResultExtractor):
    def transform_result(
        self, general_result: AggregatedResult
    ) -> Dict[str, Dict[str, NutsResult]]:
        return self._map_host_to_dest_to_nutsresult(general_result)
