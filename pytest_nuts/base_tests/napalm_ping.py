from enum import Enum

import pytest
from nornir.core import Task
from nornir.core.task import Result
from nornir_napalm.plugins.tasks import napalm_ping


class TestNapalmPing:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return napalm_ping_multi_host

    @pytest.fixture(scope="class")
    def nuts_arguments(self, nuts_parameters):
        return {"destinations_per_host": destinations_per_host(nuts_parameters['test_data']), **nuts_parameters['test_execution']}

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["source"] for entry in nuts_parameters['test_data']}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result, nuts_parameters):
        return {host: parse_ping_results(host, task_results, nuts_parameters['test_data']) for host, task_results in general_result.items()}
        # parse_ping_results should return results per host: {"destination": SUCCESS}

    @pytest.mark.nuts("source,destination,expected", "placeholder")
    def test_ping(self, transformed_result, source, destination, expected):
        assert transformed_result[source][destination].name == expected


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


def destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["source"] == host_name]


def parse_ping_results(host, task_results, test_data):
    maxdrop_per_destination = {entry["destination"]: entry["max_drop"] for entry in test_data if entry["source"] == host}
    return {ping_task.destination: map_result_to_enum(ping_task.result, maxdrop_per_destination[ping_task.destination]) for ping_task in task_results[1:]}

def map_result_to_enum(result, max_drop):
    if result['success']['packet_loss'] <= max_drop:
        return Ping.SUCCESS
    elif result['success']['packet_loss'] == result['success']['probes_sent']:
        return Ping.FAIL
    else:
        return Ping.FLAPPING
