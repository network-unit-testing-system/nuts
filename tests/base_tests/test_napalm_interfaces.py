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


@pytest.fixture
def nuts_ctx():
    return CONTEXT(None)


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_host_at_toplevel(self, nuts_ctx, general_result, host):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert host in transformed_result

    @pytest.mark.parametrize(
        "host,interface_names",
        [("R1", ["GigabitEthernet1", "GigabitEthernet2"]), ("R2", ["Loopback0", "GigabitEthernet3"])],
    )
    def test_contains_interface_names_at_second_level(self, nuts_ctx, general_result, host, interface_names):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert list(transformed_result[host].result.keys()) == interface_names

    @pytest.mark.parametrize(
        "host,name,is_enabled,is_up,mac_address",
        [
            ("R1", "GigabitEthernet1", True, True, "CA:CA:00:CE:DE:00"),
            (
                "R1",
                "GigabitEthernet2",
                False,
                True,
                "C0:FF:EE:BE:EF:00",
            ),
            ("R2", "GigabitEthernet3", False, True, "BE:EF:DE:AD:BE:EF"),
            ("R2", "Loopback0", False, False, ""),
        ],
    )
    def test_contains_information_about_interface(
        self, nuts_ctx, general_result, host, name, is_enabled, is_up, mac_address
    ):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert transformed_result[host].result[name]["is_enabled"] == is_enabled
        assert transformed_result[host].result[name]["is_up"] == is_enabled
        assert transformed_result[host].result[name]["mac_address"] == mac_address

    def test_marks_as_failed_if_task_failed(self, nuts_ctx, general_result):
        transformed_result = nuts_ctx.transform_result(general_result)
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
