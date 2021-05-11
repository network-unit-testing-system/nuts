import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_bgp_neighbors import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData, tupelize

nornir_raw_r1 = {
    "bgp_neighbors": {
        "global": {
            "router_id": "172.16.255.1",
            "peers": {
                "172.16.255.2": {
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
                "172.16.255.3": {
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
            "router_id": "172.16.255.2",
            "peers": {
                "172.16.255.1": {
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
        "local_id": "172.16.255.1",
        "peer": "172.16.255.2",
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
        "local_id": "172.16.255.1",
        "peer": "172.16.255.3",
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
        "local_id": "172.16.255.2",
        "peer": "172.16.255.1",
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
    @pytest.mark.parametrize("host", [e.test_data["host"] for e in [bgp_r1_1, bgp_r1_2, bgp_r2]])
    def test_contains_hosts_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    def test_contains_peers_at_second_level(self, transformed_result):
        r1 = bgp_r1_1.test_data["host"]
        r1_peers = [bgp_r1_1.test_data["peer"], bgp_r1_2.test_data["peer"]]
        r2 = bgp_r2.test_data["host"]
        r2_peers = bgp_r2.test_data["peer"]
        assert list(transformed_result[r1].result.keys()) == r1_peers
        assert r2_peers in transformed_result[r2].result.keys()

    def test_contains_information_about_neighbor(self, transformed_result):
        r1 = bgp_r1_1.test_data["host"]
        neighbor_details = transformed_result[r1].result[bgp_r1_1.test_data["peer"]]
        for key in bgp_r1_1.test_data:
            if key == "host" or key == "peer":
                continue
            assert bgp_r1_1.test_data[key] == neighbor_details[key]

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
