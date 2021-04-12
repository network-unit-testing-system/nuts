import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.napalm_ping import CONTEXT
from pytest_nuts.base_tests.napalm_ping import Ping
from tests.base_tests.conftest import TIMEOUT_MESSAGE
from tests.helpers.shared import create_result, create_multi_result


class Host():
    """
    Mocks nornir.core.Host class
    """
    def __init__(self, name: str):
        self.name = name


test_data = [
    {"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.3", "max_drop": 1},
    {"expected": "FAIL", "host": "R2", "destination": "172.16.23.4", "max_drop": 1},
    {"expected": "FLAPPING", "host": "R3", "destination": "172.16.23.5", "max_drop": 1},
    {"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.6", "max_drop": 1},
    {"expected": "SUCCESS", "host": "R3", "destination": "172.16.23.6", "max_drop": 1},
]

nornir_results = [
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
    task_name = "napalm_ping"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        result_content=nornir_results[0],
        host=Host("R1"),
        destination="172.16.23.3",
        task_name=task_name
    )
    result["R2"] = create_multi_result(
        result_content=nornir_results[1],
        host=Host("R2"),
        destination="172.16.23.6",
        task_name=task_name
    )

    result_r0 = Result(host=None, destination=None, result="All pings executed", name=task_name)

    multi_result_r1 = MultiResult(task_name)
    multi_result_r1.append(result_r0)
    result_r1_1 = Result(host=Host("R1"), name="napalm_ping", destination="172.16.23.3")
    result_r1_1.result = nornir_results[0]
    multi_result_r1.append(result_r1_1)
    result_r1_2 = Result(host=Host("R1"), name="napalm_ping", destination="172.16.23.6")
    result_r1_2.result = nornir_results[3]
    multi_result_r1.append(result_r1_2)
    result["R1"] = multi_result_r1

    multi_result_r2 = MultiResult(task_name)
    multi_result_r2.append(result_r0)
    result_r2 = Result(host=Host("R2"), name="napalm_ping", destination="172.16.23.4")
    result_r2.result = nornir_results[1]
    multi_result_r2.append(result_r2)
    result["R2"] = multi_result_r2

    multi_result_r3 = MultiResult(task_name)
    multi_result_r3.append(result_r0)
    result_r3 = Result(host=Host("R2"), name="napalm_ping", destination="172.16.23.5")
    result_r3.result = nornir_results[2]
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


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT(nuts_parameters={"test_data": test_data}))]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1"])
    def test_contains_host_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize("host, destination", [("R1", "172.16.23.3"), ("R2", "172.16.23.4"), ("R3", "172.16.23.5")])
    def test_contains_pinged_destination(self, transformed_result, host, destination):
        assert destination in transformed_result[host]

    @pytest.mark.parametrize("host, destination, ping_result", [("R1", "172.16.23.3", Ping.SUCCESS)])
    def test_destination_maps_to_enum_success(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize("host, destination, ping_result", [("R2", "172.16.23.4", Ping.FAIL)])
    def test_destination_maps_to_enum_failure(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize("host, destination, ping_result", [("R3", "172.16.23.5", Ping.FLAPPING)])
    def test_destination_maps_to_enum_flapping(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize(
        "host, destination, ping_result", [("R1", "172.16.23.3", Ping.SUCCESS), ("R1", "172.16.23.6", Ping.SUCCESS)]
    )
    def test_one_host_several_destinations(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"]["172.16.23.6"].failed
        assert transformed_result["R3"]["172.16.23.6"].exception is not None
