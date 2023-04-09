import pytest

from nornir.core.task import AggregatedResult
import nornir_netmiko

from nuts.base_tests.netmiko_iperf import CONTEXT
from tests.utils import create_result, create_multi_result, SelfTestData


iperf_l1_1 = SelfTestData(
    name="l1_1",
    nornir_raw_result='{"start":{"connected":[{"remote_host":"10.0.0.2"}]},\
        "end":{"sum_received":{"bits_per_second":3.298164e09}}}',
    test_data={"host": "L1", "destination": "10.0.0.2", "min_expected": 10000000},
)

iperf_l1_2 = SelfTestData(
    name="l1_2",
    nornir_raw_result='{"start":{"connected":[{"remote_host":"10.0.0.3"}]},\
        "end":{"sum_received":{"bits_per_second":3.298164e09}}}',
    test_data={"host": "L1", "destination": "10.0.0.3", "min_expected": 10000000},
)

iperf_l2_1 = SelfTestData(
    name="l2_1",
    nornir_raw_result='{"start":{"connected":[{"remote_host":"10.0.0.1"}]},\
        "end":{"sum_received":{"bits_per_second": 5000}}}',
    test_data={"host": "L2", "destination": "10.0.0.1", "min_expected": 10000000},
    expected_output=["> * assert single_result.result >= min_expected"],
    expected_outcome="failed",
)

iperf_l2_2 = SelfTestData(
    name="l2_2",
    nornir_raw_result='{"start":{"connected":[],"version":"iperf 3.1.3",\
        "system_info":"Linux"},\
        "intervals":[],"end":{},\
        "error":"error - unable to connect to server: No route to host"}',
    test_data={"host": "L2", "destination": "10.0.0.220", "min_expected": 10000000},
    expected_output=[
        "E * nuts.helpers.errors.NutsNornirError: "
        "An exception has occurred while executing nornir:",
        "*.IperfResultError: error - unable to connect to server: No route to host",
    ],
    expected_outcome="errors",
)


@pytest.fixture
def general_result():
    task_name = "netmiko_run_iperf"
    confirmation_result = create_result(result_content="iperf executed for host")
    general_result = AggregatedResult(task_name)
    general_result["L1"] = create_multi_result(
        results=[
            confirmation_result,
            iperf_l1_1.create_nornir_result(),
            iperf_l1_2.create_nornir_result(),
        ],
        task_name=task_name,
    )
    general_result["L2"] = create_multi_result(
        results=[
            confirmation_result,
            iperf_l2_1.create_nornir_result(),
            iperf_l2_2.create_nornir_result(),
        ],
        task_name=task_name,
    )
    return general_result


@pytest.fixture(
    params=[iperf_l1_1, iperf_l1_2, iperf_l2_1, iperf_l2_2],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"L1", "L2"}


def test_contains_iperf_dest(transformed_result, testdata):
    assert testdata["destination"] in transformed_result[testdata["host"]]


@pytest.mark.parametrize(
    "data, result",
    [
        pytest.param(iperf_l1_1.test_data, True, id="l1_1"),
        pytest.param(iperf_l1_2.test_data, True, id="l1_2"),
        pytest.param(iperf_l2_1.test_data, False, id="l2_1"),
    ],
)
def test_min_expected(transformed_result, data, result):
    host = data["host"]
    destination = data["destination"]
    min_expected = data["min_expected"]

    dest_result = transformed_result[host][destination]
    dest_result.validate()
    assert (dest_result.result >= min_expected) == result


def test_dest_unreachable_fails(transformed_result):
    assert transformed_result["L2"][iperf_l2_2.test_data["destination"]].failed
    assert (
        transformed_result["L2"][iperf_l2_2.test_data["destination"]].exception
        is not None
    )


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNetmikoIperf",
        task_module=nornir_netmiko,
        task_name="netmiko_send_command",
        test_count=1,
    )
