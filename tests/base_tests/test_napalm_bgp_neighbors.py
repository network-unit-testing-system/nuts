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
        "peer": R2_IP,
    },
)

bgp_r1_2 = SelfTestData(
    nornir_raw_result=nornir_raw_r1,
    test_data={
        "host": "R1",
        "peer": R3_IP,
    },
)

bgp_r2 = SelfTestData(
    nornir_raw_result=nornir_raw_r2,
    test_data={
        "host": "R2",
        "peer": R1_IP,
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


@pytest.fixture(params=[bgp_r1_1, bgp_r1_2, bgp_r2])
def raw_test_data(request):
    return request.param


def test_contains_hosts_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


@pytest.mark.parametrize("host, neighbors", [("R1", {R2_IP, R3_IP}), ("R2", {R1_IP})])
def test_contains_peers_at_second_level(transformed_result, host, neighbors):
    assert transformed_result[host].result.keys() == neighbors


def test_contains_information_about_neighbor(transformed_result, raw_test_data):
    host = raw_test_data.test_data["host"]
    peer = raw_test_data.test_data["peer"]
    neighbor_details = transformed_result[host].result[peer]
    expected = raw_test_data.nornir_raw_result["bgp_neighbors"]["global"]["peers"][peer]
    assert neighbor_details == expected


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None
