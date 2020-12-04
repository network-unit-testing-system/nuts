from typing import Dict

import pytest

from nornir.core.filter import F
from nornir.core.task import MultiResult
from nornir_netmiko import netmiko_send_command

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult


@pytest.fixture(scope="class")
def nuts_task():
    return netmiko_send_command


@pytest.fixture(scope="class")
def nuts_arguments():
    return {"command_string": "show ip ospf neighbor", "use_textfsm": True}


@pytest.fixture(scope="class")
def nuts_filter(hosts):
    return F(name__any=hosts)


@pytest.fixture(scope="class")
def hosts(destination_list):
    return {entry["source"] for entry in destination_list}


@pytest.fixture(scope="class")
def transformed_result(general_result):
    return transform_result(general_result)


@pytest.fixture
def destination_list(nuts_parameters):
    return nuts_parameters


@pytest.fixture
def single_result(transformed_result, source):
    assert source in transformed_result, f"Host {source} not found in aggregated result."
    return transformed_result[source]


@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoOspfNeighborsCount:
    @pytest.mark.nuts("source,neighbor_count")
    def test_neighbor_count(self, single_result, neighbor_count):
        assert len(single_result.result) == neighbor_count


@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoOspfNeighbors:
    @pytest.mark.nuts("source,neighbor_id")
    def test_neighbor_id(self, single_result, neighbor_id):
        assert neighbor_id in single_result.result

    @pytest.mark.nuts("source,neighbor_id,neighbor_address")
    def test_neighbor_address(self, single_result, neighbor_id, neighbor_address):
        neighbor = single_result.result[neighbor_id]
        assert neighbor["address"] == neighbor_address

    @pytest.mark.nuts("source,local_port,neighbor_id")
    def test_local_port(self, single_result, local_port, neighbor_id):
        neighbor = single_result.result[neighbor_id]
        assert neighbor["interface"] == local_port

    @pytest.mark.nuts("source,neighbor_id,state")
    def test_state(self, single_result, neighbor_id, state):
        neighbor = single_result.result[neighbor_id]
        assert neighbor["state"] == state


def transform_result(general_result) -> Dict[str, NutsResult]:
    return {source: nuts_result_wrapper(result, _transform_single_result) for source, result in general_result.items()}


def _transform_single_result(single_result: MultiResult) -> dict:
    neighbors = single_result[0].result
    return {details["neighbor_id"]: details for details in neighbors}
