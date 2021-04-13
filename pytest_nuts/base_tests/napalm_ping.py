"""Let a device ping another device."""
from enum import Enum
from typing import Dict, Callable, Any

import pytest
from nornir.core import Task
from nornir.core.filter import F
from nornir.core.task import Result, AggregatedResult
from nornir_napalm.plugins.tasks import napalm_ping

from pytest_nuts.context import NornirNutsContext
from pytest_nuts.helpers.filters import filter_hosts
from pytest_nuts.helpers.result import (
    NutsResult,
    map_host_to_dest_to_nutsresult,
)


class Ping(Enum):
    FAIL = 0
    SUCCESS = 1
    FLAPPING = 2


class PingContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return napalm_ping_multi_dests

    def nuts_arguments(self) -> dict:
        args = super().nuts_arguments()
        args["destinations_per_host"] = _destinations_per_host(self.nuts_parameters["test_data"])
        return args

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, Dict[str, NutsResult]]:
        return map_host_to_dest_to_nutsresult(general_result, self._transform_single_entry)

    def _transform_single_entry(self, single_result: Result) -> Ping:
        assert hasattr(single_result, "destination")
        assert single_result.host is not None
        max_drop = self._allowed_maxdrop_for_destination(single_result.host.name, single_result.destination)  # type: ignore[attr-defined] # see below
        return _map_result_to_enum(single_result.result, max_drop)

    def _allowed_maxdrop_for_destination(self, host: str, dest: str) -> int:
        test_data = self.nuts_parameters["test_data"]
        for entry in test_data:
            if entry["host"] == host and entry["destination"] == dest:
                return entry["max_drop"]
        return 0


CONTEXT = PingContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNapalmPing:
    @pytest.fixture
    def single_result(self, nornir_nuts_ctx: NornirNutsContext, host: str, destination: str) -> NutsResult:
        transformed_result = nornir_nuts_ctx.transformed_result()
        assert host in transformed_result, f"Host {host} not found in aggregated result."
        assert destination in transformed_result[host], f"Destination {destination} not found in result."
        return transformed_result[host][destination]

    @pytest.mark.nuts("host,destination,expected")
    def test_ping(self, single_result, expected):
        assert single_result.result.name == expected


def napalm_ping_multi_dests(task: Task, destinations_per_host, **kwargs) -> Result:
    """
    One host pings all destinations as defined in the test bundle.

    Note: The destination is not included in the nornir result if the ping fails.
    Therefore we cannot know which destination was not reachable,
    so we must patch the destination onto the result object to know later which
    host-destination pair actually failed.

    :param task: nornir task for ping
    :param destinations_per_host: all destinations one host should ping
    :param kwargs: arguments from the test bundle for the napalm ping task, such as
    count, ttl, timeout
    :return: all pinged destinations per host
    """
    destinations = destinations_per_host(task.host.name)
    for destination in destinations:
        result = task.run(task=napalm_ping, dest=destination, **kwargs)
        result[0].destination = destination  # type: ignore[attr-defined]
    return Result(host=task.host, result="All pings executed")


def _destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["host"] == host_name]


def _map_result_to_enum(result: Any, max_drop: int) -> Ping:
    assert isinstance(result, dict)
    if result["success"]["packet_loss"] == result["success"]["probes_sent"]:
        return Ping.FAIL
    if result["success"]["packet_loss"] <= max_drop:
        return Ping.SUCCESS
    else:
        return Ping.FLAPPING
