import pytest

from nornir.core.task import AggregatedResult
from nuts.base_tests.netmiko_iperf import CONTEXT
from tests.helpers.selftest_helpers import create_result, create_multi_result, SelfTestData

iperf_l1_1 = SelfTestData(
    nornir_raw_result='{"start":{"connected":[{"remote_host":"10.0.0.2"}]},"end":{"sum_received":{"bits_per_second":3.298164e09}}}',
    test_data={"host": "L1", "destination": "10.0.0.2", "min_expected": 10000000},
)

iperf_l1_2 = SelfTestData(
    nornir_raw_result='{"start":{"connected":[{"remote_host":"10.0.0.3"}]},"end":{"sum_received":{"bits_per_second":3.298164e09}}}',
    test_data={"host": "L1", "destination": "10.0.0.3", "min_expected": 10000000},
)

iperf_l2_1 = SelfTestData(
    nornir_raw_result='{"start":{"connected":[{"remote_host":"10.0.0.1"}]},"end":{"sum_received":{"bits_per_second": 5000}}}',
    test_data={"host": "L2", "destination": "10.0.0.1", "min_expected": 10000000},
)

iperf_l2_2 = SelfTestData(
    nornir_raw_result='{"start":{"connected":[],"version":"iperf 3.1.3","system_info":"Linux"},"intervals":[],"end":{},"error":"error - unable to connect to server: No route to host"}',
    test_data={"host": "L2", "destination": "10.0.0.220", "min_expected": 10000000},
)


@pytest.fixture
def general_result():
    task_name = "netmiko_run_iperf"
    confirmation_result = create_result(result_content="iperf executed for host", task_name=task_name)
    general_result = AggregatedResult(task_name)
    general_result["L1"] = create_multi_result(
        results=[
            confirmation_result,
            iperf_l1_1.create_nornir_result(task_name),
            iperf_l1_2.create_nornir_result(task_name),
        ],
        task_name=task_name,
    )
    general_result["L2"] = create_multi_result(
        results=[
            confirmation_result,
            iperf_l2_1.create_nornir_result(task_name),
            iperf_l2_2.create_nornir_result(task_name),
        ],
        task_name=task_name,
    )
    return general_result


@pytest.fixture
def all_testdata():
    return [iperf_l1_1.test_data, iperf_l1_2.test_data, iperf_l2_2.test_data, iperf_l2_2.test_data]


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    def test_contains_host_at_toplevel(self, transformed_result):
        assert all(h in transformed_result for h in ["L1", "L2"])

    def test_contains_iperf_dest(self, transformed_result, all_testdata):
        assert all(entry["destination"] in transformed_result[entry["host"]] for entry in all_testdata)

    def test_one_host_several_destinations(self, transformed_result):
        expected1 = iperf_l1_1.test_data
        expected2 = iperf_l1_2.test_data
        assert transformed_result["L1"][expected1["destination"]].result >= expected1["min_expected"]
        assert transformed_result["L1"][expected2["destination"]].result >= expected2["min_expected"]

    def test_below_min_expected_fails(self, transformed_result):
        expected1 = iperf_l2_1.test_data
        assert not transformed_result["L2"][expected1["destination"]].result >= expected1["min_expected"]

    def test_dest_unreachable_fails(self, transformed_result):
        assert transformed_result["L2"][iperf_l2_2.test_data["destination"]].failed
        assert transformed_result["L2"][iperf_l2_2.test_data["destination"]].exception is not None
