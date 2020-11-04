import pytest

from nornir.core.filter import F
from nornir_netmiko import netmiko_send_command


class TestNetmikoCdpNeighbors:

    @pytest.fixture(scope="class")
    def nuts_task(self):
        return netmiko_send_command

    @pytest.fixture(scope="class")
    def nuts_arguments(self):
        return {"command_string": "show cdp neighbors detail",
                "use_textfsm": True}

    @pytest.fixture(scope="class")
    def nuts_filter(self, hosts):
        return F(name__any=hosts)

    @pytest.fixture(scope="class")
    def hosts(self, destination_list):
        return {entry["source"] for entry in destination_list}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return {source: result[0].result for source, result in general_result.items()}

    @pytest.fixture(scope="class")
    def grouped_result(self, transformed_result):
        return {source: {neighbor['destination_host']: neighbor for neighbor in neighbors} for source, neighbors in
                transformed_result.items()}

    @pytest.fixture
    def destination_list(self, nuts_parameters):
        return nuts_parameters

    @pytest.mark.nuts("source,local_port,destination_host,management_ip,remote_port", "placeholder")
    def test_neighbor_full(self, grouped_result, source, local_port, destination_host, management_ip, remote_port):
        assert grouped_result[source][destination_host]['local_port'] == local_port
        assert grouped_result[source][destination_host]['destination_host'] == destination_host
        assert grouped_result[source][destination_host]['management_ip'] == management_ip
        assert grouped_result[source][destination_host]['remote_port'] == remote_port
