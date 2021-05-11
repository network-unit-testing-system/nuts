import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_network_instances import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData

nornir_raw_result_r1 = {
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
        "space": {
            "name": "space",
            "type": "L3VRF",
            "state": {"route_distinguisher": ""},
            "interfaces": {"interface": {}},
        },
        "ship": {
            "name": "ship",
            "type": "L3VRF",
            "state": {"route_distinguisher": "1:1"},
            "interfaces": {"interface": {"Loopback2": {}}},
        },
    }
}

nornir_raw_result_r2 = {
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


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result([create_result(nornir_raw_result_r1, task_name)], task_name)
    result["R2"] = create_multi_result([create_result(nornir_raw_result_r2, task_name)], task_name)
    result["R3"] = timeouted_multiresult
    return result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    def test_contains_hosts_at_toplevel(self, transformed_result):
        assert all(h in transformed_result for h in ["R1", "R2"])

    def test_contains_network_instances_at_second_level(self, transformed_result):
        assert all(
            network_instances in transformed_result["R1"].result
            for network_instances in ["default", "mgmt", "space", "ship"]
        )
        assert all(network_instances in transformed_result["R2"].result for network_instances in ["default", "mgmt"])

    def test_contains_interfaces_at_network_instance(self, transformed_result):
        assert transformed_result["R1"].result["default"]["interfaces"] == [
            "GigabitEthernet2",
            "GigabitEthernet3",
            "GigabitEthernet4",
            "GigabitEthernet5",
            "Loopback0",
        ]
        assert transformed_result["R2"].result["mgmt"]["interfaces"] == ["GigabitEthernet1"]

    def test_contains_route_distinguisher_at_network_instance(self, transformed_result):
        assert transformed_result["R1"].result["default"]["route_distinguisher"] == ""
        assert transformed_result["R1"].result["ship"]["route_distinguisher"] == "1:1"
        assert transformed_result["R2"].result["mgmt"]["route_distinguisher"] == ""

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
