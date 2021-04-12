import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.netmiko_ospf_neighbors import CONTEXT
from tests.helpers.shared import create_multi_result, create_result

neighbor_details = {
    "neighbor_id": "172.16.255.3",
    "priority": "1",
    "state": "FULL/BDR",
    "dead_time": "00:00:33",
    "address": "172.16.13.3",
    "interface": "GigabitEthernet4",
}

nornir_results = [
    [
        neighbor_details.copy(),
        {
            "neighbor_id": "172.16.255.2",
            "priority": "1",
            "state": "FULL/BDR",
            "dead_time": "00:00:32",
            "address": "172.16.12.2",
            "interface": "GigabitEthernet3",
        },
        {
            "neighbor_id": "172.16.255.4",
            "priority": "1",
            "state": "FULL/BDR",
            "dead_time": "00:00:32",
            "address": "172.16.14.4",
            "interface": "GigabitEthernet2",
        },
    ],
    [
        {
            "neighbor_id": "172.16.255.3",
            "priority": "1",
            "state": "FULL/BDR",
            "dead_time": "00:00:34",
            "address": "172.16.23.3",
            "interface": "GigabitEthernet4",
        },
        {
            "neighbor_id": "172.16.255.11",
            "priority": "1",
            "state": "FULL/BDR",
            "dead_time": "00:00:35",
            "address": "172.16.211.11",
            "interface": "GigabitEthernet3",
        },
        {
            "neighbor_id": "172.16.255.1",
            "priority": "1",
            "state": "FULL/DR",
            "dead_time": "00:00:33",
            "address": "172.16.12.1",
            "interface": "GigabitEthernet2",
        },
    ],
]


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "netmiko_send_command"
    results_per_host = [[create_result(result, task_name)] for result in nornir_results]
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(results_per_host[0], task_name)
    result["R2"] = create_multi_result(results_per_host[1], task_name)
    result["R3"] = timeouted_multiresult
    return result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_hosts_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize(
        "host,network_instances",
        [
            ("R1", ["172.16.255.3", "172.16.255.2", "172.16.255.4"]),
            ("R2", ["172.16.255.3", "172.16.255.11", "172.16.255.1"]),
        ],
    )
    def test_contains_neighbors_at_second_level(self, transformed_result, host, network_instances):
        assert list(transformed_result[host].result.keys()) == network_instances

    @pytest.mark.parametrize("host, neighbor, details", [("R1", "172.16.255.3", neighbor_details)])
    def test_contains_information_about_neighbor(self, transformed_result, host, neighbor, details):
        expected_details = transformed_result[host].result[neighbor]
        for key in details:
            assert expected_details[key] == details[key]

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
