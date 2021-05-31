import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_bgp_neighbors import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, SelfTestData

R1_IP = "172.16.255.1"
R2_IP = "172.16.255.2"
R3_IP = "172.16.255.3"

nornir_raw_r1 = {
    "bgp_neighbors": {
        "global": {
            "router_id": R1_IP,
            "peers": {
                R2_IP: {
                    "local_as": 45001,
                    "remote_as": 45002,
                    "remote_id": "0.0.0.0",
                    "is_up": False,
                    "is_enabled": True,
                    "description": "",
                    "uptime": -1,
                    "address_family": {
                        "ipv4 unicast": {"received_prefixes": -1, "accepted_prefixes": -1, "sent_prefixes": -1}
                    },
                },
                R3_IP: {
                    "local_as": 45001,
                    "remote_as": 45003,
                    "remote_id": "0.0.0.0",
                    "is_up": False,
                    "is_enabled": True,
                    "description": "",
                    "uptime": -1,
                    "address_family": {
                        "ipv4 unicast": {"received_prefixes": -1, "accepted_prefixes": -1, "sent_prefixes": -1}
                    },
                },
            },
        }
    }
}

nornir_raw_r2 = {
    "bgp_neighbors": {
        "global": {
            "router_id": R2_IP,
            "peers": {
                R1_IP: {
                    "local_as": 45002,
                    "remote_as": 45001,
                    "remote_id": "0.0.0.0",
                    "is_up": False,
                    "is_enabled": True,
                    "description": "",
                    "uptime": -1,
                    "address_family": {
                        "ipv4 unicast": {"received_prefixes": -1, "accepted_prefixes": -1, "sent_prefixes": -1}
                    },
                }
            },
        }
    }
}


bgp_r1_1 = SelfTestData(
    nornir_raw_result=nornir_raw_r1,
    test_data={
        "host": "R1",
        "local_id": R1_IP,
        "peer": R2_IP,
        "is_enabled": True,
        "remote_as": 45002,
        "remote_id": "0.0.0.0",
        "local_as": 45001,
        "is_up": False,
    },
)

bgp_r1_2 = SelfTestData(
    nornir_raw_result=nornir_raw_r1,
    test_data={
        "host": "R1",
        "local_id": R1_IP,
        "peer": R3_IP,
        "is_enabled": True,
        "remote_as": 45001,
        "remote_id": "0.0.0.0",
        "local_as": 45002,
        "is_up": False,
    },
)

bgp_r2 = SelfTestData(
    nornir_raw_result=nornir_raw_r2,
    test_data={
        "host": "R2",
        "local_id": R2_IP,
        "peer": R1_IP,
        "is_enabled": True,
        "remote_as": 45001,
        "remote_id": "0.0.0.0",
        "local_as": 45002,
        "is_up": False,
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        results=[bgp_r1_1.create_nornir_result(task_name), bgp_r1_2.create_nornir_result(task_name)],
        task_name=task_name,
    )
    result["R2"] = create_multi_result(results=[bgp_r2.create_nornir_result(task_name)], task_name=task_name)
    result["R3"] = timeouted_multiresult
    return result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    def test_contains_hosts_at_toplevel(self, transformed_result):
        assert transformed_result.keys() == {"R1", "R2", "R3"}

    @pytest.mark.parametrize("host, neighbors", [("R1", {R2_IP, R3_IP}), ("R2", {R1_IP})])
    def test_contains_peers_at_second_level(self, transformed_result, host, neighbors):
        assert transformed_result[host].result.keys() == neighbors

    def test_contains_information_about_neighbor(self, transformed_result):
        neighbor_details = transformed_result["R1"].result[bgp_r1_1.test_data["peer"]]
        expected = {
            "address_family": {"ipv4 unicast": {"accepted_prefixes": -1, "received_prefixes": -1, "sent_prefixes": -1}},
            "description": "",
            "is_enabled": bgp_r1_1.test_data["is_enabled"],
            "is_up": bgp_r1_1.test_data["is_up"],
            "local_as": bgp_r1_1.test_data["local_as"],
            "local_id": R1_IP,
            "remote_as": bgp_r1_1.test_data["remote_as"],
            "remote_id": bgp_r1_1.test_data["remote_id"],
            "uptime": -1,
        }
        assert neighbor_details == expected

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
