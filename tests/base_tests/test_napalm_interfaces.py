import pytest
from nornir.core.task import AggregatedResult

from pytest_nuts.base_tests.napalm_interfaces import CONTEXT
from tests.helpers.shared import create_multi_result


@pytest.fixture
def general_result(timeouted_multiresult):
    result = AggregatedResult("napalm_get")
    result["R1"] = create_multi_result(
        {
            "interfaces": {
                "GigabitEthernet1": {
                    "is_enabled": True,
                    "is_up": True,
                    "description": "",
                    "mac_address": "CA:CA:00:CE:DE:00",
                    "last_flapped": -1.0,
                    "mtu": 1500,
                    "speed": 1000,
                },
                "GigabitEthernet2": {
                    "is_enabled": False,
                    "is_up": True,
                    "description": "",
                    "mac_address": "C0:FF:EE:BE:EF:00",
                    "last_flapped": -1.0,
                    "mtu": 1500,
                    "speed": 1000,
                },
            },
        }
    )

    result["R2"] = create_multi_result(
        {
            "interfaces": {
                "Loopback0": {
                    "is_enabled": True,
                    "is_up": False,
                    "description": "",
                    "mac_address": "",
                    "last_flapped": -1.0,
                    "mtu": 1514,
                    "speed": 8000,
                },
                "GigabitEthernet3": {
                    "is_enabled": False,
                    "is_up": False,
                    "description": "",
                    "mac_address": "BE:EF:DE:AD:BE:EF",
                    "last_flapped": -1.0,
                    "mtu": 1500,
                    "speed": 1000,
                },
            }
        }
    )
    result["R3"] = timeouted_multiresult
    return result

# apply mark at module-level: https://docs.pytest.org/en/stable/example/markers.html#marking-whole-classes-or-modules
pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT(nuts_parameters=None))]

class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_host_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize(
        "host, interface_name",
        [("R1", "GigabitEthernet1"), ("R1", "GigabitEthernet2"), ("R2", "Loopback0"), ("R2", "GigabitEthernet3")],
    )
    def test_contains_interface_names_at_second_level(self, transformed_result, host, interface_name):
        assert interface_name in transformed_result[host].result.keys()

    @pytest.mark.parametrize(
        "host, name, is_enabled, is_up, mac_address",
        [
            ("R1", "GigabitEthernet1", True, True, "CA:CA:00:CE:DE:00"),
            ("R1", "GigabitEthernet2", False, True, "C0:FF:EE:BE:EF:00"),
            ("R2", "Loopback0", True, False, ""),
            ("R2", "GigabitEthernet3", False, False, "BE:EF:DE:AD:BE:EF"),
        ],
    )
    def test_contains_information_about_interface(
        self, transformed_result, host, name, is_enabled, is_up, mac_address
    ):
        interface_result = transformed_result[host].result[name]
        assert interface_result["is_enabled"] == is_enabled
        assert interface_result["is_up"] == is_up
        assert interface_result["mac_address"] == mac_address

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
