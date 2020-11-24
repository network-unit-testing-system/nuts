from enum import Enum
from typing import Dict, List, Callable

import pytest
from nornir.core import Task
from nornir.core.task import Result, MultiResult
from nornir_napalm.plugins.tasks import napalm_ping

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult, check_result


@pytest.mark.usefixtures("check_result")
class TestNapalmPing:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return napalm_ping_multi_host

    @pytest.fixture(scope="class")
    def nuts_arguments(self, nuts_parameters):
        return {
            "destinations_per_host": _destinations_per_host(nuts_parameters["test_data"]),
            **nuts_parameters["test_execution"],
        }

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["source"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result, nuts_parameters):
        return transform_result(general_result, nuts_parameters["test_data"])

    @pytest.fixture
    def single_result(self, transformed_result, source, destination):
        assert source in transformed_result, f"Host {source} not found in aggregated result."
        assert destination in transformed_result[source], f"Destination {destination} not found in result."
        return transformed_result[source][destination]

    @pytest.mark.nuts("source,destination,expected")
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
        result[0].destination = destination
    return Result(host=task.host, result="All pings executed")


def _destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["source"] == host_name]


def transform_result(general_result, test_data) -> Dict[str, Dict[str, NutsResult]]:
    return {host: _parse_ping_results(host, task_results, test_data) for host, task_results in general_result.items()}


def _parse_ping_results(host: str, task_results: MultiResult, test_data: List[dict]) -> dict:
    maxdrop_per_destination = {
        entry["destination"]: entry["max_drop"] for entry in test_data if entry["source"] == host
    }
    return {
        ping_task.destination: nuts_result_wrapper(
            ping_task, _get_transform_single_entry(maxdrop_per_destination[ping_task.destination])
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
