"""Let a device ping another device."""
from enum import Enum
from typing import Dict, Callable, Any, List

import pytest
from nornir.core import Task
from nornir.core.filter import F
from nornir.core.task import Result
from nornir_napalm.plugins.tasks import napalm_ping

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import (
    NutsResult,
    AbstractHostDestResultExtractor,
)


class Ping(Enum):
    FAIL = 0
    SUCCESS = 1
    FLAPPING = 2


class PingExtractor(AbstractHostDestResultExtractor):
    def single_transform(self, single_result: Result) -> Ping:
        assert single_result.host is not None
        assert single_result.result is not None
        max_drop = self._allowed_max_drop_for_destination(
            single_result.host.name,
            single_result.destination,  # type: ignore[attr-defined] # see below
        )
        return self._map_result_to_enum(single_result.result, max_drop)

    def _allowed_max_drop_for_destination(self, host: str, dest: str) -> int:
        """
        Matches the host-destination pair from a nornir task to the
        host-destination pair from test_data and retrieves its
        max_drop value that has been defined for that pair.

        :param host: host entry from the nornir task
        :param dest: destination that was pinged by a host from the nornir task
        :return: max_drop value from test_data
        """
        test_data: List[Dict[str, Any]] = self._nuts_ctx.nuts_parameters["test_data"]
        for entry in test_data:
            if entry["host"] == host and entry["destination"] == dest:
                return entry["max_drop"]
        return 0

    def _map_result_to_enum(
        self, result: Dict[str, Dict[Any, Any]], max_drop: int
    ) -> Ping:
        """
        Evaluates the ping that has been conducted with nornir and matches it
        to a Ping-Enum which can be either FAIL, SUCCESS or FLAPPING.

        FAIL: Packet loss equals probes sent.
        SUCCESS: Packet loss is below or equal max_drop.
        FLAPPING: Everything else.

        :param result: a single nornir Result
        :param max_drop: max_drop threshold
        :return: evaluated ping result
        """
        if result["success"]["packet_loss"] == result["success"]["probes_sent"]:
            return Ping.FAIL
        if result["success"]["packet_loss"] <= max_drop:
            return Ping.SUCCESS
        else:
            return Ping.FLAPPING

    def single_result(self, nuts_test_entry: Dict[str, Any]) -> NutsResult:
        host = nuts_test_entry["host"]
        destination = nuts_test_entry["destination"]
        assert (
            host in self.transformed_result
        ), f"Host {host} not found in aggregated result."
        assert (
            destination in self.transformed_result[host]
        ), f"Destination {destination} not found in result."
        return self.transformed_result[host][destination]


class PingContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return self.napalm_ping_multi_dests

    def napalm_ping_multi_dests(self, task: Task, **kwargs: Any) -> Result:
        """
        One host pings all destinations as defined in the test bundle.

        Note: The destination is not included in the nornir result if the ping fails.
        Therefore we cannot know which destination was not reachable,
        so we must patch the destination onto the result object to know later which
        host-destination pair actually failed.

        :param task: nornir task for ping
        :param kwargs: arguments from the test bundle for the napalm ping task, such as
        count, ttl, timeout
        :return: all pinged destinations per host
        """
        destinations_per_hosts = [
            entry["destination"]
            for entry in self.nuts_parameters["test_data"]
            if entry["host"] == task.host.name
        ]
        for destination in destinations_per_hosts:
            result = task.run(task=napalm_ping, dest=destination, **kwargs)
            result[0].destination = destination  # type: ignore[attr-defined]
        return Result(host=task.host, result="All pings executed")

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> PingExtractor:
        return PingExtractor(self)


CONTEXT = PingContext


class TestNapalmPing:
    @pytest.mark.nuts("expected")
    def test_ping(self, single_result, expected):
        assert single_result.result.name == expected
