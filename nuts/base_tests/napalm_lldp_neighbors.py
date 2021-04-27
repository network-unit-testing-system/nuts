"""Query LLDP neighbors of a device."""
from typing import Dict, Callable, List

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.converters import InterfaceNameConverter
from nuts.helpers.result import nuts_result_wrapper, NutsResult


class LldpNeighborsContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List]:
        return {"getters": ["lldp_neighbors_detail"]}

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, NutsResult]:
        return {
            host: nuts_result_wrapper(result, self._transform_host_results) for host, result in general_result.items()
        }

    def _transform_host_results(self, single_result: MultiResult) -> dict:
        assert single_result[0].result is not None
        task_result = single_result[0].result
        neighbors = task_result["lldp_neighbors_detail"]
        return {peer: self._add_custom_fields(details[0]) for peer, details in neighbors.items()}

    def _add_custom_fields(self, element: dict) -> dict:
        element = self._add_expanded_remote_port(element)
        element = self._add_remote_host(element)
        return element

    def _add_remote_host(self, element: dict) -> dict:
        element["remote_host"] = element["remote_system_name"]
        return element

    def _add_expanded_remote_port(self, element: dict) -> dict:
        element["remote_port_expanded"] = InterfaceNameConverter().expand_interface_name(element["remote_port"])
        return element


CONTEXT = LldpNeighborsContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNapalmLldpNeighbors:
    @pytest.mark.nuts("host,local_port,remote_host")
    def test_remote_host(self, single_result, local_port, remote_host):
        lldp_neighbor_entry = single_result.result[local_port]
        assert lldp_neighbor_entry["remote_host"] == remote_host

    @pytest.mark.nuts("host,local_port,remote_port")
    def test_remote_port(self, single_result, local_port, remote_port):
        lldp_neighbor_entry = single_result.result[local_port]
        assert (
            lldp_neighbor_entry["remote_port"] == remote_port
            or lldp_neighbor_entry["remote_port_expanded"] == remote_port
        )
