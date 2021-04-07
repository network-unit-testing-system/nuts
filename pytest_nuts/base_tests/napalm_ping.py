"""Let a device ping another device."""
from enum import Enum
from typing import Dict, List, Callable, Optional

import pytest
from nornir.core import Task
from nornir.core.filter import F
from nornir.core.task import Result, MultiResult, AggregatedResult
from nornir_napalm.plugins.tasks import napalm_ping

from pytest_nuts.context import NornirNutsContext
from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult


class PingContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return napalm_ping_multi_host

    def nuts_arguments(self) -> dict:
        args = super().nuts_arguments()
        args["destinations_per_host"] = _destinations_per_host(self.nuts_parameters["test_data"])
        return args

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, Dict[str, NutsResult]]:

        return {host: self._transform_host_results(task_results) for host, task_results in general_result.items()}

    def _allowed_maxdrop_for_destination(self, host: str, dest: str) -> int:
        test_data = self.nuts_parameters["test_data"]
        for entry in test_data:
            if entry["host"] == host and entry["destination"] == dest:
                return entry["max_drop"]
        return 0

    def _transform_single_entry(self, single_result: Result):
        assert hasattr(single_result, "destination")
        max_drop = self._allowed_maxdrop_for_destination(single_result.host.name, single_result.destination)
        return _map_result_to_enum(single_result.result, max_drop)

    def _transform_host_results(self, task_results: MultiResult) -> dict:
        return {
            single_result.destination: nuts_result_wrapper(single_result, self._transform_single_entry)
            for single_result in task_results[1:]
        }




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


class Ping(Enum):
    FAIL = 0
    SUCCESS = 1
    FLAPPING = 2


def napalm_ping_multi_host(task: Task, destinations_per_host, **kwargs) -> Result:
    destinations = destinations_per_host(task.host.name)
    for destination in destinations:
        result = task.run(task=napalm_ping, dest=destination, **kwargs)
        # the destination is not included in the nornir result if the ping fails
        # therefore we cannot know which destination was not reachable
        # so we must patch the destination onto the result object to know later which
        # host-destination pair actually failed
        result[0].destination = destination  # type: ignore[attr-defined]
    return Result(host=task.host, result="All pings executed")


def _destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["host"] == host_name]


def _map_result_to_enum(result: dict, max_drop: int) -> Ping:
    if result["success"]["packet_loss"] == result["success"]["probes_sent"]:
        return Ping.FAIL
    if result["success"]["packet_loss"] <= max_drop:
        return Ping.SUCCESS
    else:
        return Ping.FLAPPING
