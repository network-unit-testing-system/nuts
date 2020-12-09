import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.napalm_ping import transform_result
from pytest_nuts.base_tests.napalm_ping import Ping
from tests.base_tests.conftest import TIMEOUT_MESSAGE
from tests.helpers.shared import create_result

test_data = [
    {"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.3", "max_drop": 1},
    {"expected": "FAIL", "host": "R2", "destination": "172.16.23.4", "max_drop": 1},
    {"expected": "FLAPPING", "host": "R3", "destination": "172.16.23.5", "max_drop": 1},
    {"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.6", "max_drop": 1},
    {"expected": "SUCCESS", "host": "R3", "destination": "172.16.23.6", "max_drop": 1},
]

result_data = [
    {
        "success": {
            "probes_sent": 5,
            "packet_loss": 1,
            "rtt_min": 1.0,
            "rtt_max": 2.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
            ],
        }
    },
    {
        "success": {
            "probes_sent": 5,
            "packet_loss": 5,
            "rtt_min": 1.0,
            "rtt_max": 1.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
            ],
        }
    },
    {
        "success": {
            "probes_sent": 5,
            "packet_loss": 3,
            "rtt_min": 1.0,
            "rtt_max": 1.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
            ],
        }
    },
    {
        "success": {
            "probes_sent": 5,
            "packet_loss": 1,
            "rtt_min": 1.0,
            "rtt_max": 2.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
            ],
        }
    },
]


@pytest.fixture
def general_result():
    result = AggregatedResult("napalm_ping_multi_host")
    result_r0 = Result(host=None, destination=None, result="All pings executed", name="napalm_ping_multi_host")

    multi_result_r1 = MultiResult("napalm_ping_multi_host")
    multi_result_r1.append(result_r0)
    result_r1_1 = Result(host=None, name="napalm_ping", destination="172.16.23.3")
    result_r1_1.result = result_data[0]
    multi_result_r1.append(result_r1_1)
    result_r1_2 = Result(host=None, name="napalm_ping", destination="172.16.23.6")
    result_r1_2.result = result_data[3]
    multi_result_r1.append(result_r1_2)
    result["R1"] = multi_result_r1

    multi_result_r2 = MultiResult("napalm_ping_multi_host")
    multi_result_r2.append(result_r0)
    result_r2 = Result(host=None, name="napalm_ping", destination="172.16.23.4")
    result_r2.result = result_data[1]
    multi_result_r2.append(result_r2)
    result["R2"] = multi_result_r2

    multi_result_r3 = MultiResult("napalm_ping_multi_host")
    multi_result_r3.append(result_r0)
    result_r3 = Result(host=None, name="napalm_ping", destination="172.16.23.5")
    result_r3.result = result_data[2]
    multi_result_r3.append(result_r3)
    multi_result_r3.append(
        create_result(
            TIMEOUT_MESSAGE,
            failed=True,
            exception=ConnectionException("Cannot connect to 10.20.0.123"),
            destination="172.16.23.6",
        )
    )
    result["R3"] = multi_result_r3
    return result


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1"])
    def test_contains_host_at_toplevel(self, general_result, host):
        transformed_result = transform_result(general_result, test_data)
        assert host in transformed_result

    @pytest.mark.parametrize("host,destination", [("R1", "172.16.23.3"), ("R2", "172.16.23.4"), ("R3", "172.16.23.5")])
    def test_contains_pinged_destination(self, general_result, host, destination):
        transformed_result = transform_result(general_result, test_data)
        assert destination in transformed_result[host]

    @pytest.mark.parametrize("host,destination,ping_result", [("R1", "172.16.23.3", Ping.SUCCESS)])
    def test_destination_maps_to_enum_success(self, general_result, host, destination, ping_result):
        transformed_result = transform_result(general_result, test_data)
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize("host,destination,ping_result", [("R2", "172.16.23.4", Ping.FAIL)])
    def test_destination_maps_to_enum_failure(self, general_result, host, destination, ping_result):
        transformed_result = transform_result(general_result, test_data)
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize("host,destination,ping_result", [("R3", "172.16.23.5", Ping.FLAPPING)])
    def test_destination_maps_to_enum_flapping(self, general_result, host, destination, ping_result):
        transformed_result = transform_result(general_result, test_data)
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize(
        "host, destination,ping_result", [("R1", "172.16.23.3", Ping.SUCCESS), ("R1", "172.16.23.6", Ping.SUCCESS)]
    )
    def test_one_host_several_destinations(self, general_result, host, destination, ping_result):
        transformed_result = transform_result(general_result, test_data)
        assert transformed_result[host][destination].result == ping_result

    def test_marks_as_failed_if_task_failed(self, general_result):
        transformed_result = transform_result(general_result, test_data)
        assert transformed_result["R3"]["172.16.23.6"].failed
        assert transformed_result["R3"]["172.16.23.6"].exception is not None
