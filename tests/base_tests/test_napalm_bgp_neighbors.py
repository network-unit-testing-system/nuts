import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_bgp_neighbors import CONTEXT
from tests.helpers.shared import create_multi_result, create_result

neighbor_details = {
    "local_as": 45001,
    "remote_as": 45002,
    "remote_id": "0.0.0.0",
    "is_up": False,
    "is_enabled": True,
    "description": "",
    "uptime": -1,
    "address_family": {"ipv4 unicast": {"received_prefixes": -1, "accepted_prefixes": -1, "sent_prefixes": -1}},
}

nornir_results = [
    {
        "bgp_neighbors": {
            "global": {
                "router_id": "172.16.255.1",
                "peers": {
                    "172.16.255.2": neighbor_details.copy(),
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
    },
    {
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
    },
]


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    results_per_host = [[create_result(result, task_name)] for result in nornir_results]
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(results_per_host[0], task_name)
    result["R2"] = create_multi_result(results_per_host[1], task_name)
    result["R3"] = timeouted_multiresult
    return result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2", "R3"])
    def test_contains_hosts_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize("host, neighbors", [("R1", ["172.16.255.2", "172.16.255.3"]), ("R2", ["172.16.255.1"])])
    def test_contains_peers_at_second_level(self, transformed_result, host, neighbors):
        assert list(transformed_result[host].result.keys()) == neighbors

    @pytest.mark.parametrize("host, neighbor, details", [("R1", "172.16.255.2", neighbor_details)])
    def test_contains_information_about_neighbor(self, transformed_result, host, neighbor, details):
        expected_details = transformed_result[host].result[neighbor]
        for key in details:
            assert expected_details[key] == details[key]

    @pytest.mark.parametrize("host, neighbor, local_id", [("R1", "172.16.255.2", "172.16.255.1")])
    def test_contains_router_id_as_local_id(self, transformed_result, host, neighbor, local_id):
        assert transformed_result[host].result[neighbor]["local_id"] == local_id

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
