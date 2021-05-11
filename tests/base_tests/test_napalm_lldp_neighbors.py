import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_lldp_neighbors import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData

nornir_raw_result_r1 = {
    "lldp_neighbors_detail": {
        "GigabitEthernet4": [
            {
                "remote_chassis_id": "001e.e611.3500",
                "remote_port": "Gi2",
                "remote_port_description": "test12345",
                "remote_system_name": "R3",
                "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
                "remote_system_capab": ["bridge", "router"],
                "remote_system_enable_capab": ["router"],
                "parent_interface": "",
            }
        ],
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

nornir_raw_result_r2 = {
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

lldp_r1_1 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "local_port": "GigabitEthernet4", "remote_host": "R3", "remote_port": "GigabitEthernet2"},
)

lldp_r1_2 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "local_port": "GigabitEthernet3", "remote_host": "R2", "remote_port": "GigabitEthernet2"},
)

lldp_r2_1 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r2,
    test_data={"host": "R2", "local_port": "GigabitEthernet4", "remote_host": "R3", "remote_port": "GigabitEthernet3"},
)

lldp_r2_2 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r2,
    test_data={"host": "R2", "local_port": "GigabitEthernet2", "remote_host": "R1", "remote_port": "GigabitEthernet3"},
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    results_per_host = [[create_result(result, task_name)] for result in nornir_results]
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(results_per_host[0], task_name)
    result["R2"] = create_multi_result(results_per_host[1], task_name)
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture
def all_testdata():
    return [lldp_r1_1.test_data, lldp_r1_2.test_data, lldp_r2_1.test_data, lldp_r2_2.test_data]


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    def test_contains_hosts_at_toplevel(self, transformed_result):
        assert all(h in transformed_result for h in ["R1", "R2", "R3"])

    def test_contains_results_with_ports_at_second_level(self, transformed_result, all_testdata):
        assert all(entry["local_port"] in transformed_result[entry["host"]].result for entry in all_testdata)

    def test_contains_failed_result_at_second_level_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception

    def test_contains_information_about_neighbor(self, transformed_result):
        expected_details = lldp_r1_1.test_data
        actual_details = transformed_result["R1"].result["GigabitEthernet4"]
        assert actual_details["remote_host"] == expected_details["remote_host"]
        assert (
            actual_details["remote_port"] == expected_details["remote_port"]
            or actual_details["remote_port_expanded"] == expected_details["remote_port"]
        )

    def test_contains_information_remote_host(self, transformed_result):
        expected_details = lldp_r1_1.test_data
        assert transformed_result["R1"].result["GigabitEthernet4"]["remote_host"] == expected_details["remote_host"]

    def test_contains_information_expanded_interface(self, transformed_result):
        expected_details1 = lldp_r1_1.test_data
        expected_details2 = lldp_r1_2.test_data
        assert (
            transformed_result["R1"].result["GigabitEthernet4"]["remote_port_expanded"]
            == expected_details1["remote_port"]
        )
        assert (
            transformed_result["R1"].result["GigabitEthernet4"]["remote_port_expanded"]
            == expected_details2["remote_port"]
        )
