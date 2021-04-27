"""Query CDP neighbors of a device."""
from typing import Callable, Dict

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult
from nornir_netmiko import netmiko_send_command

from nuts.helpers.result import nuts_result_wrapper, NutsResult
from nuts.context import NornirNutsContext


class CdpNeighborsContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return netmiko_send_command

    def nuts_arguments(self) -> dict:
        return {"command_string": "show cdp neighbors detail", "use_textfsm": True}

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def _transform_host_results(self, host_results: MultiResult) -> dict:
        assert host_results[0].result is not None
        return {neighbor["destination_host"]: neighbor for neighbor in host_results[0].result}

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, NutsResult]:
        return {
            host: nuts_result_wrapper(result, self._transform_host_results) for host, result in general_result.items()
        }


CONTEXT = CdpNeighborsContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoCdpNeighbors:
    @pytest.mark.nuts("host,remote_host")
    def test_remote_host(self, single_result, remote_host):
        assert remote_host in single_result.result

    @pytest.mark.nuts("host,remote_host,local_port")
    def test_local_port(self, single_result, remote_host, local_port):
        assert single_result.result[remote_host]["local_port"] == local_port

    @pytest.mark.nuts("host,remote_host,remote_port")
    def test_remote_port(self, single_result, remote_host, remote_port):
        assert single_result.result[remote_host]["remote_port"] == remote_port

    @pytest.mark.nuts("host,remote_host,management_ip")
    def test_management_ip(self, single_result, remote_host, management_ip):
        assert single_result.result[remote_host]["management_ip"] == management_ip
