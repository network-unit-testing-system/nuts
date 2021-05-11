from typing import Dict, List, Any

import pytest

from nornir.core.task import AggregatedResult
from nuts.base_tests.netmiko_iperf import CONTEXT
from tests.helpers.selftest_helpers import create_result, create_multi_result

test_data_and_nornir_results: List[Dict[Any, Any]] = [
    {
        "test_data": {"host": "L1", "destination": "10.0.0.2", "min_expected": 10000000},
        "nornir_result": '{"start":{"connected":[{"remote_host":"10.0.0.2"}]},"end":{"sum_received":{"bits_per_second":3.298164e09}}}',
    },
    {
        "test_data": {"host": "L1", "destination": "10.0.0.3", "min_expected": 10000000},
        "nornir_result": '{"start":{"connected":[{"remote_host":"10.0.0.3"}]},"end":{"sum_received":{"bits_per_second":3.298164e09}}}',
    },
    {
        "test_data": {"host": "L2", "destination": "10.0.0.1", "min_expected": 10000000},
        "nornir_result": '{"start":{"connected":[{"remote_host":"10.0.0.1"}]},"end":{"sum_received":{"bits_per_second": 5000}}}',
    },
    {
        "test_data": {"host": "L2", "destination": "10.0.0.220", "min_expected": 10000000},
        "nornir_result": '{	"start":{"connected":[],"version":"iperf 3.1.3","system_info":"Linux"},"intervals":[],"end":{},"error":"error - unable to connect to server: No route to host"}',
    },
]

reachable_hosts = [tuple(entry["test_data"].values()) for entry in test_data_and_nornir_results[:-1]]


@pytest.fixture
def general_result():
    task_name = "netmiko_run_iperf"
    results = [
        create_result(
            data["nornir_result"],
            task_name,
            host=data["test_data"]["host"],
            destination=data["test_data"]["destination"],
        )
        for data in test_data_and_nornir_results
    ]
    confirmation_result = create_result(result_content="iperf executed for host", task_name=task_name)
    general_result = AggregatedResult(task_name)
    general_result["L1"] = create_multi_result(
        results=[confirmation_result, results[0], results[1]], task_name=task_name
    )
    general_result["L2"] = create_multi_result(
        results=[confirmation_result, results[2], results[3]], task_name=task_name
    )
    return general_result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["L1"])
    def test_contains_host_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize("host, destination, min_expected", reachable_hosts)
    def test_contains_iperf_dest(self, transformed_result, host, destination, min_expected):
        assert destination in transformed_result[host]

    @pytest.mark.parametrize("host, destination, min_expected", reachable_hosts[:1])
    def test_one_host_several_destinations(self, transformed_result, host, destination, min_expected):
        assert transformed_result[host][destination].result >= min_expected

    @pytest.mark.parametrize("host, destination, min_expected", [reachable_hosts[2]])
    def test_below_min_expected_fails(self, transformed_result, host, destination, min_expected):
        assert not transformed_result[host][destination].result >= min_expected

    @pytest.mark.parametrize(
        "host, destination, min_expected", [tuple(test_data_and_nornir_results[3]["test_data"].values())]
    )
    def test_dest_unreachable_failes(self, transformed_result, host, destination, min_expected):
        assert transformed_result[host][destination].failed
        assert transformed_result[host][destination].exception is not None
