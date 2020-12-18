import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.netmiko_iperf import transform_result
from tests.helpers.shared import create_result

test_data = [
    {"host": "L1", "destination": "10.0.0.2", "min_expected": 10000000},
    {"host": "L1", "destination": "10.0.0.3", "min_expected": 10000000},
    {"host": "L2", "destination": "10.0.0.1", "min_expected": 10000000},
]

result_data = [
    {
        "start": {
            "connected": [
                {
                    "remote_host": "10.0.0.2",
                }
            ],
        },
        "end": {
            "sum_received": {"bits_per_second": 3.298164e09},
        },
    },
    {
        "start": {
            "connected": [
                {
                    "remote_host": "10.0.0.3",
                }
            ],
        },
        "end": {
            "sum_received": {"bits_per_second": 3.298164e09},
        },
    },
    {
        "start": {
            "connected": [
                {
                    "remote_host": "10.0.0.1",
                }
            ],
        },
        "end": {
            "sum_received": {"bits_per_second": 0},
        },
    }
]

@pytest.fixture
def general_result():
    result = AggregatedResult("netmiko_iperf")

    multi_result_l1 = MultiResult("netmiko_run_iperf")
    result_0 = Result(host=None, name="netmiko_run_iperf", result="iperf executed")
    multi_result_l1.append(result_0)
    result_l1_1 = Result(host=None, name="netmiko_send_command")
    result_l1_1.result = result_data[0]
    multi_result_l1.append(result_l1_1)
    result_l1_2 = Result(host=None, name="netmiko_send_command")
    result_l1_2.result = result_data[1]
    multi_result_l1.append(result_l1_2)
    result["L1"] = multi_result_l1

    multi_result_l2 = MultiResult("netmiko_run_iperf")
    multi_result_l2.append(result_0)
    result_l2_1 = Result(host=None, name="netmiko_send_command")
    result_l2_1.result = result_data[2]
    result["L2"] = multi_result_l2

    return result

class TestTransformResult:
    @pytest.mark.parametrize("host", ["L1"])
    def test_contains_host_at_toplevel(self, general_result, host):
        transformed_result = transform_result(general_result)
        assert host in transformed_result

