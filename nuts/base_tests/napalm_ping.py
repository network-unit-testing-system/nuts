"""Let a device ping another device."""
from enum import Enum
from typing import Dict, List, Callable

import pytest
from nornir.core import Task
from nornir.core.filter import F
from nornir.core.task import Result, MultiResult, AggregatedResult
from nornir_napalm.plugins.tasks import napalm_ping

from nuts.context import NornirNutsContext
from nuts.helpers.result import nuts_result_wrapper, NutsResult


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
        test_data = self.nuts_parameters["test_data"]
        return {
            host: _parse_ping_results(host, task_results, test_data) for host, task_results in general_result.items()
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
        result[0].destination = destination  # type: ignore[attr-defined]
    return Result(host=task.host, result="All pings executed")


def _destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["host"] == host_name]


def _parse_ping_results(host: str, task_results: MultiResult, test_data: List[dict]) -> dict:
    maxdrop_per_destination = {
        entry["destination"]: entry.get("max_drop", 0) for entry in test_data if entry["host"] == host
    }
    return {
        ping_task.destination: nuts_result_wrapper(  # type: ignore[attr-defined]
            ping_task, _get_transform_single_entry(maxdrop_per_destination[ping_task.destination])  # type: ignore[attr-defined]
        )
        for ping_task in task_results[1:]
    }


def _get_transform_single_entry(max_drop):
    return lambda ping_task: _map_result_to_enum(ping_task.result, max_drop)


def _map_result_to_enum(result: dict, max_drop: int) -> Ping:
    if result["success"]["packet_loss"] == result["success"]["probes_sent"]:
        return Ping.FAIL
    if result["success"]["packet_loss"] <= max_drop:
        return Ping.SUCCESS
    else:
        return Ping.FLAPPING
