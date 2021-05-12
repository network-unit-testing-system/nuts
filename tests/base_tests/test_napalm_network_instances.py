import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_network_instances import CONTEXT
from tests.helpers.shared import create_multi_result


@pytest.fixture
def general_result(timeouted_multiresult):
    result = AggregatedResult("napalm_get")
    result["R1"] = create_multi_result(
        {
            "network_instances": {
                "default": {
                    "name": "default",
                    "type": "DEFAULT_INSTANCE",
                    "state": {"route_distinguisher": ""},
                    "interfaces": {
                        "interface": {
                            "GigabitEthernet2": {},
                            "GigabitEthernet3": {},
                            "GigabitEthernet4": {},
                            "GigabitEthernet5": {},
                            "Loopback0": {},
                        }
                    },
                },
                "mgmt": {
                    "name": "mgmt",
                    "type": "L3VRF",
                    "state": {"route_distinguisher": ""},
                    "interfaces": {"interface": {"GigabitEthernet1": {}}},
                },
                "test": {
                    "name": "test",
                    "type": "L3VRF",
                    "state": {"route_distinguisher": ""},
                    "interfaces": {"interface": {}},
                },
                "test2": {
                    "name": "test2",
                    "type": "L3VRF",
                    "state": {"route_distinguisher": "1:1"},
                    "interfaces": {"interface": {"Loopback2": {}}},
                },
            }
        }
    )
    result["R2"] = create_multi_result(
        {
            "network_instances": {
                "default": {
                    "name": "default",
                    "type": "DEFAULT_INSTANCE",
                    "state": {"route_distinguisher": ""},
                    "interfaces": {
                        "interface": {
                            "GigabitEthernet2": {},
                            "GigabitEthernet3": {},
                            "GigabitEthernet4": {},
                            "Loopback0": {},
                        }
                    },
                },
                "mgmt": {
                    "name": "mgmt",
                    "type": "L3VRF",
                    "state": {"route_distinguisher": ""},
                    "interfaces": {"interface": {"GigabitEthernet1": {}}},
                },
            }
        }
    )
    result["R3"] = timeouted_multiresult
    return result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_hosts_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize(
        "host, network_instances", [("R1", ["default", "mgmt", "test", "test2"]), ("R2", ["default", "mgmt"])]
    )
    def test_contains_network_instances_at_second_level(self, transformed_result, host, network_instances):
        assert list(transformed_result[host].result) == network_instances

    @pytest.mark.parametrize(
        "host, network_instance, interfaces",
        [
            (
                "R1",
                "default",
                ["GigabitEthernet2", "GigabitEthernet3", "GigabitEthernet4", "GigabitEthernet5", "Loopback0"],
            ),
            ("R2", "mgmt", ["GigabitEthernet1"]),
        ],
    )
    def test_contains_interfaces_at_network_instance(self, transformed_result, host, network_instance, interfaces):

        assert transformed_result[host].result[network_instance]["interfaces"] == interfaces

    @pytest.mark.parametrize(
        "host, network_instance, route_distinguisher",
        [
            ("R1", "default", ""),
            ("R1", "test2", "1:1"),
            ("R2", "mgmt", ""),
        ],
    )
    def test_contains_route_distinguisher_at_network_instance(
        self, transformed_result, host, network_instance, route_distinguisher
    ):
        assert transformed_result[host].result[network_instance]["route_distinguisher"] == route_distinguisher

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
