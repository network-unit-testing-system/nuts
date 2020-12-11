from typing import Dict

import pytest

from nornir.core.filter import F
from nornir.core.task import MultiResult
from nornir_netmiko import netmiko_send_command

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult
from pytest_nuts.plugin import NutsContext


class CdpNeighborsContext(NutsContext):

    def nuts_task(self):
        return netmiko_send_command

    def nuts_arguments(self):
        return {"command_string": "show cdp neighbors detail", "use_textfsm": True}

    def nornir_filter(self):
        breakpoint()
        hosts = {entry["host"] for entry in self.nuts_parameters}
        return F(name__any=hosts)

    def _transform_host_results(self, host_results: MultiResult) -> dict:
        return {neighbor["destination_host"]: neighbor for neighbor in host_results[0].result}

    def transformed_result(self):
        general_result = self.general_result()
        return {host: nuts_result_wrapper(result, self._transform_host_results) for host, result in general_result.items()}

    def single_result(self, host):
        transformed_result = self.transformed_result()
        assert host in transformed_result, f"Host {host} not found in aggregated result."
        return transformed_result[host]


CONTEXT = CdpNeighborsContext


#@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoCdpNeighbors:

    @pytest.mark.nuts("host,remote_host")
    def test_remote_host(self, nuts_ctx, host, remote_host):
        assert remote_host in nuts_ctx.single_result(host).result

    @pytest.mark.nuts("host,remote_host,local_port")
    def test_local_port(self, nuts_ctx, host, remote_host, local_port):
        assert nuts_ctx.single_result(host).result[remote_host]["local_port"] == local_port

    @pytest.mark.nuts("host,remote_host,remote_port")
    def test_remote_port(self, nuts_ctx, host, remote_host, remote_port):
        assert nuts_ctx.single_result(host).result[remote_host]["remote_port"] == remote_port

    @pytest.mark.nuts("host,remote_host,management_ip")
    def test_management_ip(self, nuts_ctx, host, remote_host, management_ip):
        assert nuts_ctx.single_result(host).result[remote_host]["management_ip"] == management_ip
