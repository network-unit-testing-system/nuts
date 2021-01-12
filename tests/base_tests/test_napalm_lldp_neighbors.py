import pytest
from nornir.core.task import AggregatedResult

from pytest_nuts.base_tests.napalm_lldp_neighbors import CONTEXT
from tests.helpers.shared import create_multi_result

neighbor_details = {
    "remote_chassis_id": "001e.e611.3500",
    "remote_port": "Gi2",
    "remote_port_description": "test12345",
    "remote_system_name": "R3",
    "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
    "remote_system_capab": ["bridge", "router"],
    "remote_system_enable_capab": ["router"],
    "parent_interface": "",
}


@pytest.fixture
def nuts_ctx():
    return CONTEXT(None)


@pytest.fixture
def general_result(timeouted_multiresult):
    result = AggregatedResult("napalm_get")
    result["R1"] = create_multi_result(
        {
            "lldp_neighbors_detail": {
                "GigabitEthernet4": [neighbor_details.copy()],
                "GigabitEthernet3": [
                    {
                        "remote_chassis_id": "001e.f62f.a600",
                        "remote_port": "Gi2",
                        "remote_port_description": "GigabitEthernet2",
                        "remote_system_name": "R2",
                        "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
                        "remote_system_capab": ["bridge", "router"],
                        "remote_system_enable_capab": ["router"],
                        "parent_interface": "",
                    }
                ],
            }
        }
    )
    result["R2"] = create_multi_result(
        {
            "lldp_neighbors_detail": {
                "GigabitEthernet4": [
                    {
                        "remote_chassis_id": "001e.e611.3500",
                        "remote_port": "Gi3",
                        "remote_port_description": "GigabitEthernet3",
                        "remote_system_name": "R3",
                        "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
                        "remote_system_capab": ["bridge", "router"],
                        "remote_system_enable_capab": ["router"],
                        "parent_interface": "",
                    }
                ],
                "GigabitEthernet2": [
                    {
                        "remote_chassis_id": "001e.e547.df00",
                        "remote_port": "Gi3",
                        "remote_port_description": "GigabitEthernet3",
                        "remote_system_name": "R1",
                        "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
                        "remote_system_capab": ["bridge", "router"],
                        "remote_system_enable_capab": ["router"],
                        "parent_interface": "",
                    }
                ],
            }
        }
    )

    result["R3"] = timeouted_multiresult
    return result


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2", "R3"])
    def test_contains_hosts_at_toplevel(self, nuts_ctx, general_result, host):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert host in transformed_result

    @pytest.mark.parametrize(
        "host,local_ports",
        [("R1", ["GigabitEthernet4", "GigabitEthernet3"]), ("R2", ["GigabitEthernet4", "GigabitEthernet2"])],
    )
    def test_contains_results_with_ports_at_second_level(self, nuts_ctx, general_result, host, local_ports):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert list(transformed_result[host].result.keys()) == local_ports

    @pytest.mark.parametrize(
        "host,local_ports",
        [("R3", ["GigabitEthernet4"])],
    )
    def test_contains_failed_result_at_second_level_if_task_failed(self, nuts_ctx, general_result, host, local_ports):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert transformed_result[host].failed
        assert transformed_result[host].exception

    @pytest.mark.parametrize("host,local_port,expected_details", [("R1", "GigabitEthernet4", neighbor_details)])
    def test_contains_information_about_neighbor(self, nuts_ctx, general_result, host, local_port, expected_details):
        transformed_result = nuts_ctx.transform_result(general_result)
        actual_details = transformed_result[host].result[local_port]
        for key in expected_details:
            assert actual_details[key] == expected_details[key]

    @pytest.mark.parametrize("host,local_port,remote_host", [("R1", "GigabitEthernet4", "R3")])
    def test_contains_information_remote_host(self, nuts_ctx, general_result, host, local_port, remote_host):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert transformed_result[host].result[local_port]["remote_host"] == remote_host

    @pytest.mark.parametrize("host,local_port,remote_port_expanded", [("R1", "GigabitEthernet4", "GigabitEthernet2")])
    def test_contains_information_expanded_interface(
        self, nuts_ctx, general_result, host, local_port, remote_port_expanded
    ):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert transformed_result[host].result[local_port]["remote_port_expanded"] == remote_port_expanded
