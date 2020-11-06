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
        test_data = nuts_parameters['test_data']
        return {"destinations_per_host": destinations_per_host(test_data)}

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["source"] for entry in nuts_parameters['test_data']}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return {host: parse_ping_results(task_results) for host, task_results in general_result.items()}

    @pytest.mark.nuts("source,destination,expected", "placeholder")
    def test_ping(self, transformed_result, source, destination, expected):
        assert transformed_result[source][destination].name == expected


class Ping(Enum):
    FAIL = 0
    SUCCESS = 1
    FLAPPING = 2


def napalm_ping_multi_host(task: Task, destinations_per_host) -> Result:
    destinations = destinations_per_host(task.host.name)
    for destination in destinations:
        result = task.run(task=napalm_ping, dest=destination)
        result[0].destination = destination
    return Result(host=task.host, result="All pings executed")


def destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["source"] == host_name]


def parse_ping_results(task_results):
    return {ping_task.destination: parse_result(ping_task.result['success']) for ping_task in task_results[1:]}


def parse_result(result):
    if result['packet_loss'] == 0:
        return Ping.SUCCESS
    if result['packet_loss'] == result['probes_sent']:
        return Ping.FAIL
    return Ping.FLAPPING
