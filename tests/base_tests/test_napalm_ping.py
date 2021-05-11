import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult, MultiResult, Result

from nuts.base_tests.napalm_ping import CONTEXT
from nuts.base_tests.napalm_ping import Ping
from tests.base_tests.conftest import TIMEOUT_MESSAGE
from tests.helpers.selftest_helpers import create_result, create_multi_result, Host

test_data_and_nornir_results = [
    {
        "test_data": {"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.3", "max_drop": 1},
        "nornir_result": {
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
    },
    {
        "test_data": {"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.6", "max_drop": 1},
        "nornir_result": {
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
    },
    {
        "test_data": {"expected": "FAIL", "host": "R2", "destination": "172.16.23.4", "max_drop": 1},
        "nornir_result": {
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
    },
    {
        "test_data": {"expected": "FLAPPING", "host": "R3", "destination": "172.16.23.5", "max_drop": 1},
        "nornir_result": {
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
    },
]


@pytest.fixture
def general_result():
    task_name = "napalm_ping"
    results = [
        create_result(
            data["nornir_result"],
            task_name,
            host=data["test_data"]["host"],
            destination=data["test_data"]["destination"],
        )
        for data in test_data_and_nornir_results
    ]
    confirmation_result = create_result(result_content="All pings executed", task_name="napalm_ping_multihost")
    timeouted = create_result(
        TIMEOUT_MESSAGE,
        task_name=task_name,
        host="R3",
        destination="172.16.23.6",
        failed=True,
        exception=ConnectionException("Cannot connect to 10.20.0.123"),
    )
    general_result = AggregatedResult(task_name)
    general_result["R1"] = create_multi_result(
        results=[confirmation_result, results[0], results[1]], task_name=task_name
    )
    general_result["R2"] = create_multi_result(results=[confirmation_result, results[2]], task_name=task_name)
    general_result["R3"] = create_multi_result(
        results=[confirmation_result, results[3], timeouted], task_name=task_name
    )
    return general_result


test_data = [data["test_data"] for data in test_data_and_nornir_results]
pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT(nuts_parameters={"test_data": test_data}))]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1"])
    def test_contains_host_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize("host, destination", [("R1", "172.16.23.3"), ("R1", "172.16.23.6"), ("R3", "172.16.23.5")])
    def test_contains_pinged_destination(self, transformed_result, host, destination):
        assert destination in transformed_result[host].keys()

    @pytest.mark.parametrize("host, destination, ping_result", [("R1", "172.16.23.3", Ping.SUCCESS)])
    def test_destination_maps_to_enum_success(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize("host, destination, ping_result", [("R2", "172.16.23.4", Ping.FAIL)])
    def test_destination_maps_to_enum_failure(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize("host, destination, ping_result", [("R1", "172.16.23.6", Ping.FLAPPING)])
    def test_destination_maps_to_enum_flapping(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    @pytest.mark.parametrize(
        "host, destination, ping_result", [("R1", "172.16.23.3", Ping.SUCCESS), ("R1", "172.16.23.6", Ping.FLAPPING)]
    )
    def test_one_host_several_destinations(self, transformed_result, host, destination, ping_result):
        assert transformed_result[host][destination].result == ping_result

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"]["172.16.23.6"].failed
        assert transformed_result["R3"]["172.16.23.6"].exception is not None
