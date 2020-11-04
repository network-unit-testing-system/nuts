from enum import Enum

import pytest

from nornir.core import Task
from nornir.core.task import MultiResult
from nornir_napalm.plugins.tasks import napalm_ping


class TestNapalmPing:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return napalm_ping_multi_host

    @pytest.fixture(scope="class")
    def nuts_arguments(self, nuts_parameters):
        test_data = nuts_parameters['test_data']
        delay_factor = nuts_parameters['test_execution']['delay_factor']
        return {"destinations_per_host": destinations_per_host(test_data),
                "delay_factor": delay_factor}

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["source"] for entry in nuts_parameters['test_data']}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return map_result_to_enum(general_result)

    @pytest.mark.nuts("source,destination,expected", "placeholder")
    def test_ping(self, transformed_result, source, destination, expected):
        assert transformed_result[source][destination].name == expected


class Ping(Enum):
    FAIL = 0
    SUCCESS = 1
    FLAPPING = 2


def napalm_ping_multi_host(task: Task, destinations_per_host, delay_factor) -> MultiResult:
    destinations = destinations_per_host(task.host.name)
    results = MultiResult("pinged_hosts")
    for destination in destinations:
        results.append(
            task.run(
                task=napalm_ping,
                dest=destination,
                delay_factor=delay_factor,
            )
        )
    return results


def destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["source"] == host_name]


def map_result_to_enum(general_result: dict):
    nornir_answer_by_host = {key: [v.result for v in value[1:]] for key, value in general_result.items()}
    # TODO nornir/napalm returns an empty list of results when the host does not exist on the network, instead of the required IP
    # destination: trans[<dict: hosts>][<list:dests>]['success']['results'][<list of result of 5 pings>: 0]['ip_address']
    # result of ping that must be mapped to enum: trans["R1"][0]['success']['packet_loss']
    return None


