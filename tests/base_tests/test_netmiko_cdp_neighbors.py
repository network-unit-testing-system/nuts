import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.netmiko_cdp_neighbors import transform_result

neighbor_details = {
    "destination_host": "R2",
    "management_ip": "172.16.12.2",
    "platform": "cisco CSR1000V",
    "remote_port": "GigabitEthernet2",
    "local_port": "GigabitEthernet3",
    "software_version": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
    "capabilities": "Router IGMP",
}


@pytest.fixture
def general_result(timeouted_multiresult):
    result = AggregatedResult("netmiko_send_command")
    multi_result_r1 = MultiResult("netmiko_send_command")
    result_r1 = Result(host=None, name="netmiko_send_command")
    result_r1.result = [
        neighbor_details.copy(),
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

    multi_result_r1.append(result_r1)
    result["R1"] = multi_result_r1
    multi_result_r2 = MultiResult("netmiko_send_command")
    result_r2 = Result(host=None, name="naplam_get")
    result_r2.result = [
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
    multi_result_r2.append(result_r2)
    result["R2"] = multi_result_r2
    result["R3"] = timeouted_multiresult
    return result


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_hosts_at_toplevel(self, general_result, host):
        transformed_result = transform_result(general_result)
        assert host in transformed_result

    @pytest.mark.parametrize(
        "host,network_instances",
        [
            ("R1", ["R2", "R3", "R4"]),
            ("R2", ["R3", "R1", "R5"]),
        ],
    )
    def test_contains_neighbors_at_second_level(self, general_result, host, network_instances):
        transformed_result = transform_result(general_result)
        assert list(transformed_result[host].result.keys()) == network_instances

    @pytest.mark.parametrize("host,neighbor,details", [("R1", "R2", neighbor_details)])
    def test_contains_information_about_neighbor(self, general_result, host, neighbor, details):
        transformed_result = transform_result(general_result)
        expected_details = transformed_result[host].result[neighbor]
        for key in details:
            assert expected_details[key] == details[key]

    def test_marks_as_failed_if_task_failed(self, general_result):
        transformed_result = transform_result(general_result)
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
