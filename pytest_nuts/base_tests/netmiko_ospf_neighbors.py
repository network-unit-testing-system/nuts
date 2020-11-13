import pytest

from nornir.core.filter import F
from nornir_netmiko import netmiko_send_command


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


class TestNetmikoCdpNeighborsCount:
    @pytest.mark.nuts("source,neighbor_count", "placeholder")
    def test_neighbor_count(self, transformed_result, source, neighbor_count):
        assert source in transformed_result
        assert len(transformed_result[source]) == neighbor_count


class TestNetmikoCdpNeighborsFull:
    @pytest.mark.nuts("source,local_port,neighbor_id,neighbor_address,state", "placeholder")
    def test_neighbor_full(self, transformed_result, source, local_port, neighbor_id, neighbor_address, state):
        assert source in transformed_result
        assert neighbor_id in transformed_result[source]
        neighbor = transformed_result[source][neighbor_id]
        assert neighbor["interface"] == local_port
        assert neighbor["address"] == neighbor_address
        assert neighbor["state"] == state

def transform_result(general_result):
    return {source: _transform_single_result(result) for source, result in general_result.items()}


def _transform_single_result(single_result):
    neighbors = single_result[0].result
    return {details["neighbor_id"]: details for details in neighbors}
