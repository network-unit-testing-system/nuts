import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.napalm_lldp_neighbors import transform_result

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
def general_result():
    result = AggregatedResult("napalm_get")
    multi_result_r1 = MultiResult("napalm_get")
    result_r1 = Result(host=None, name="naplam_get")
    result_r1.result = {
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
    multi_result_r1.append(result_r1)
    result["R1"] = multi_result_r1
    multi_result_r2 = MultiResult("napalm_get")
    result_r2 = Result(host=None, name="naplam_get")
    result_r2.result = {
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
    multi_result_r2.append(result_r2)
    result["R2"] = multi_result_r2
    return result


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_hosts_at_toplevel(self, general_result, host):
        transformed_result = transform_result(general_result)
        assert host in transformed_result

    @pytest.mark.parametrize(
        "host,local_ports",
        [("R1", ["GigabitEthernet4", "GigabitEthernet3"]), ("R2", ["GigabitEthernet4", "GigabitEthernet2"])],
    )
    def test_contains_local_ports_at_second_level(self, general_result, host, local_ports):
        transformed_result = transform_result(general_result)
        assert list(transformed_result[host].keys()) == local_ports

    @pytest.mark.parametrize("host,local_port,expected_details", [("R1", "GigabitEthernet4", neighbor_details)])
    def test_contains_information_about_neighbor(self, general_result, host, local_port, expected_details):
        transformed_result = transform_result(general_result)
        actual_details = transformed_result[host][local_port]
        for key in expected_details:
            assert actual_details[key] == expected_details[key]

    @pytest.mark.parametrize("host,local_port,remote_host", [("R1", "GigabitEthernet4", "R3")])
    def test_contains_information_remote_host(self, general_result, host, local_port, remote_host):
        transformed_result = transform_result(general_result)
        assert transformed_result[host][local_port]["remote_host"] == remote_host

    @pytest.mark.parametrize("host,local_port,remote_port_expanded", [("R1", "GigabitEthernet4", "GigabitEthernet2")])
    def test_contains_information_expanded_interface(self, general_result, host, local_port, remote_port_expanded):
        transformed_result = transform_result(general_result)
        assert transformed_result[host][local_port]["remote_port_expanded"] == remote_port_expanded
