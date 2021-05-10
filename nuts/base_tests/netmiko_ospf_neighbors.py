"""Query OSPF neighbors of a device or count them."""
from typing import Callable, Dict

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult
from nornir_netmiko import netmiko_send_command

from nuts.context import NornirNutsContext
from nuts.helpers.result import nuts_result_wrapper, NutsResult


class OspfNeighborsContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return netmiko_send_command

    def nuts_arguments(self) -> dict:
        return {"command_string": "show ip ospf neighbor", "use_textfsm": True}

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def _transform_host_results(self, single_result: MultiResult) -> dict:
        assert single_result[0].result is not None
        neighbors = single_result[0].result
        return {details["neighbor_id"]: details for details in neighbors}

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, NutsResult]:
        return {
            host: nuts_result_wrapper(result, self._transform_host_results) for host, result in general_result.items()
        }


CONTEXT = OspfNeighborsContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoOspfNeighborsCount:
    @pytest.mark.nuts("host,neighbor_count")
    def test_neighbor_count(self, single_result, neighbor_count):
        assert len(single_result.result) == neighbor_count


@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoOspfNeighbors:
    @pytest.mark.nuts("host,neighbor_id")
    def test_neighbor_id(self, single_result, neighbor_id):
        assert neighbor_id in single_result.result

    @pytest.mark.nuts("host,neighbor_id,neighbor_address")
    def test_neighbor_address(self, single_result, neighbor_id, neighbor_address):
        neighbor = single_result.result[neighbor_id]
        assert neighbor["address"] == neighbor_address

    @pytest.mark.nuts("host,local_port,neighbor_id")
    def test_local_port(self, single_result, local_port, neighbor_id):
        neighbor = single_result.result[neighbor_id]
        assert neighbor["interface"] == local_port

    @pytest.mark.nuts("host,neighbor_id,state")
    def test_state(self, single_result, neighbor_id, state):
        neighbor = single_result.result[neighbor_id]
        assert neighbor["state"] == state
