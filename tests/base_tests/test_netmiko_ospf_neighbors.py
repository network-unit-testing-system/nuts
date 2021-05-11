import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from nuts.base_tests.netmiko_ospf_neighbors import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result

raw_nornir_result_r1 = [
    {
        "neighbor_id": "172.16.255.3",
        "priority": "1",
        "state": "FULL/BDR",
        "dead_time": "00:00:33",
        "address": "172.16.13.3",
        "interface": "GigabitEthernet4",
    },
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
]

raw_nornir_result_r2 = [
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
        assert all(n in transformed_result["R1"].result for n in ["172.16.255.3", "172.16.255.2", "172.16.255.4"])
        assert all(n in transformed_result["R2"].result for n in ["172.16.255.3", "172.16.255.11", "172.16.255.1"])

    def test_contains_information_about_neighbor(self, transformed_result):
        details = {
            "neighbor_id": "172.16.255.3",
            "priority": "1",
            "state": "FULL/BDR",
            "dead_time": "00:00:33",
            "address": "172.16.13.3",
            "interface": "GigabitEthernet4",
        }
        expected_details = transformed_result["R1"].result["172.16.255.3"]
        for key in details:
            assert expected_details[key] == details[key]

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
