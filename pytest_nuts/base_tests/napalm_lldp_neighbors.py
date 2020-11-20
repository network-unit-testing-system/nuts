import pytest
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get

from pytest_nuts.helpers.converters import InterfaceNameConverter
from pytest_nuts.helpers.result import nuts_result_wrapper, check_result


@pytest.mark.usefixtures("check_result")
class TestNapalmLldpNeighbors:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return napalm_get

    @pytest.fixture(scope="class")
    def nuts_arguments(self):
        return {"getters": ["lldp_neighbors_detail"]}

    @pytest.fixture(scope="class")
    def nornir_filter(self, hosts):
        return F(name__any=hosts)

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["source"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return transform_result(general_result)

    @pytest.fixture
    def single_result(self, transformed_result, source):
        assert source in transformed_result, f"Host {source} not found in aggregated result."
        return transformed_result[source]

    @pytest.mark.nuts("source,local_port,remote_host,remote_port", "placeholder")
    def test_neighbor_full(self, single_result, local_port, remote_host, remote_port):
        bgp_neighbor_entry = single_result.result[local_port]
        assert bgp_neighbor_entry["remote_host"] == remote_host
        assert (
            bgp_neighbor_entry["remote_port"] == remote_port
            or bgp_neighbor_entry["remote_port_expanded"] == remote_port
        )


def transform_result(general_result):
    return {source: nuts_result_wrapper(result, _transform_single_result) for source, result in general_result.items()}


def _transform_single_result(single_result):
    task_result = single_result[0].result
    neighbors = task_result["lldp_neighbors_detail"]
    return {peer: _add_custom_fields(details[0]) for peer, details in neighbors.items()}


def _add_custom_fields(element):
    element = _add_expanded_remote_port(element)
    element = _add_remote_host(element)
    return element


def _add_remote_host(element):
    element["remote_host"] = element["remote_system_name"]
    return element


def _add_expanded_remote_port(element):
    element["remote_port_expanded"] = InterfaceNameConverter().expand_interface_name(element["remote_port"])
    return element
