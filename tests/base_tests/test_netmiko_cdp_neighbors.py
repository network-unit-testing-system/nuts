import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from nuts.base_tests.netmiko_cdp_neighbors import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result

raw_nornir_result_r1 = [
    {
        "destination_host": "R2",
        "management_ip": "172.16.12.2",
        "platform": "cisco CSR1000V",
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet3",
        "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
        "capabilities": "Router IGMP",
    },
    {
        "destination_host": "R3",
        "management_ip": "172.16.13.3",
        "platform": "cisco CSR1000V",
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet4",
        "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
        "capabilities": "Router IGMP",
    },
    {
        "destination_host": "R4",
        "management_ip": "172.16.14.4",
        "platform": "cisco CSR1000V",
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet2",
        "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
        "capabilities": "Router IGMP",
    },
]

raw_nornir_result_r2 = [
    {
        "destination_host": "R3",
        "management_ip": "172.16.23.3",
        "platform": "cisco CSR1000V",
        "remote_port": "GigabitEthernet3",
        "local_port": "GigabitEthernet4",
        "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
        "capabilities": "Router IGMP",
    },
    {
        "destination_host": "R1",
        "management_ip": "172.16.12.1",
        "platform": "cisco CSR1000V",
        "remote_port": "GigabitEthernet3",
        "local_port": "GigabitEthernet2",
        "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
        "capabilities": "Router IGMP",
    },
    {
        "destination_host": "R5",
        "management_ip": "172.16.211.11",
        "platform": "cisco CSR1000V",
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet3",
        "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
        "capabilities": "Router IGMP",
    },
]


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "netmiko_send_command"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result([create_result(raw_nornir_result_r1, task_name)], task_name)
    result["R2"] = create_multi_result([create_result(raw_nornir_result_r2, task_name)], task_name)
    result["R3"] = timeouted_multiresult
    return result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    def test_contains_hosts_at_toplevel(self, transformed_result):
        assert all(h in transformed_result for h in ["R1", "R2"])

    def test_contains_neighbors_at_second_level(self, transformed_result):
        assert all(network_instances in transformed_result["R1"].result for network_instances in ["R2", "R3", "R4"])
        assert all(network_instances in transformed_result["R2"].result for network_instances in ["R3", "R1", "R5"])

    def test_contains_information_about_neighbor(self, transformed_result):
        expected_details = transformed_result["R1"].result["R2"]
        details = {
            "destination_host": "R2",
            "management_ip": "172.16.12.2",
            "platform": "cisco CSR1000V",
            "remote_port": "GigabitEthernet2",
            "local_port": "GigabitEthernet3",
            "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
            "capabilities": "Router IGMP",
        }
        for key in details:
            assert expected_details[key] == details[key]

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
