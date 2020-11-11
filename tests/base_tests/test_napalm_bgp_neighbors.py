import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.napalm_bgp_neighbors import transform_result

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


@pytest.fixture
def general_result():
    result = AggregatedResult("napalm_get")
    multi_result_r1 = MultiResult("napalm_get")
    result_r1 = Result(host=None, name="napalm_get")
    result_r1.result = {
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
    }
    multi_result_r1.append(result_r1)
    result["R1"] = multi_result_r1
    multi_result_r2 = MultiResult("napalm_get")
    result_r2 = Result(host=None, name="napalm_get")
    result_r2.result = {
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
    multi_result_r2.append(result_r2)
    result["R2"] = multi_result_r2
    return result


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_hosts_at_toplevel(self, general_result, host):
        transformed_result = transform_result(general_result)
        assert host in transformed_result

    @pytest.mark.parametrize("host,neighbors", [("R1", ["172.16.255.2", "172.16.255.3"]), ("R2", ["172.16.255.1"])])
    def test_contains_peers_at_second_level(self, general_result, host, neighbors):
        transformed_result = transform_result(general_result)
        assert list(transformed_result[host].keys()) == neighbors

    @pytest.mark.parametrize("host,neighbor,details", [("R1", "172.16.255.2", neighbor_details)])
    def test_contains_information_about_neighbor(self, general_result, host, neighbor, details):
        transformed_result = transform_result(general_result)
        expected_details = transformed_result[host][neighbor]
        for key in details:
            assert expected_details[key] == details[key]

    @pytest.mark.parametrize("host,neighbor,local_id", [("R1", "172.16.255.2", "172.16.255.1")])
    def test_contains_router_id_as_local_id(self, general_result, host, neighbor, local_id):
        transformed_result = transform_result(general_result)
        assert transformed_result[host][neighbor]["local_id"] == local_id
