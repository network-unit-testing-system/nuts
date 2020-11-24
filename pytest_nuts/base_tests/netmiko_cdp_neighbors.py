from typing import Dict

import pytest

from nornir.core.filter import F
from nornir.core.task import MultiResult
from nornir_netmiko import netmiko_send_command

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult

# noinspection PyUnresolvedReferences
from pytest_nuts.helpers.result import check_result


@pytest.mark.usefixtures("check_result")
class TestNetmikoCdpNeighbors:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return netmiko_send_command

    @pytest.fixture(scope="class")
    def nuts_arguments(self):
        return {"command_string": "show cdp neighbors detail", "use_textfsm": True}

    @pytest.fixture(scope="class")
    def nuts_filter(self, hosts):
        return F(name__any=hosts)

    @pytest.fixture(scope="class")
    def hosts(self, destination_list):
        return {entry["source"] for entry in destination_list}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return transform_result(general_result)

    @pytest.fixture
    def single_result(self, transformed_result, source):
        assert source in transformed_result, f"Host {source} not found in aggregated result."
        return transformed_result[source]

    @pytest.fixture
    def destination_list(self, nuts_parameters):
        return nuts_parameters

    @pytest.mark.nuts("source,destination_host")
    def test_destination_host(self, single_result, destination_host):
        assert destination_host in single_result.result

    @pytest.mark.nuts("source,destination_host,local_port")
    def test_local_port(self, single_result, destination_host, local_port):
        assert single_result.result[destination_host]["local_port"] == local_port

    @pytest.mark.nuts("source,destination_host,remote_port")
    def test_remote_port(self, single_result, destination_host, remote_port):
        assert single_result.result[destination_host]["remote_port"] == remote_port

    @pytest.mark.nuts("source,destination_host,management_ip")
    def test_management_ip(self, single_result, destination_host, management_ip):
        assert single_result.result[destination_host]["management_ip"] == management_ip


def transform_result(general_result) -> Dict[str, NutsResult]:
    return {source: nuts_result_wrapper(result, _transform_single_result) for source, result in general_result.items()}


def _transform_single_result(single_result: MultiResult) -> dict:
    return {neighbor["destination_host"]: neighbor for neighbor in single_result[0].result}
