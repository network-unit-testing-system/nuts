import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_ping import CONTEXT
from tests.base_tests.conftest import TIMEOUT_MESSAGE
from tests.utils import create_result, create_multi_result, SelfTestData

IP_3 = "172.16.23.3"
IP_4 = "172.16.23.4"
IP_5 = "172.16.23.5"
IP_6 = "172.16.23.6"

ping_r1_1 = SelfTestData(
    name="r1_1",
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 1,
            "rtt_min": 1.0,
            "rtt_max": 2.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": IP_3, "rtt": 0.0},
                {"ip_address": IP_3, "rtt": 0.0},
                {"ip_address": IP_3, "rtt": 0.0},
                {"ip_address": IP_3, "rtt": 0.0},
                {"ip_address": IP_3, "rtt": 0.0},
            ],
        }
    },
    test_data={"expected": "SUCCESS", "host": "R1", "destination": IP_3, "max_drop": 1},
)

ping_r1_2 = SelfTestData(
    name="r1_2",
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 1,
            "rtt_min": 1.0,
            "rtt_max": 1.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
            ],
        }
    },
    test_data={"expected": "SUCCESS", "host": "R1", "destination": IP_5, "max_drop": 1},
)

ping_r2 = SelfTestData(
    name="r2",
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 5,
            "rtt_min": 1.0,
            "rtt_max": 1.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": IP_4, "rtt": 0.0},
                {"ip_address": IP_4, "rtt": 0.0},
                {"ip_address": IP_4, "rtt": 0.0},
                {"ip_address": IP_4, "rtt": 0.0},
                {"ip_address": IP_4, "rtt": 0.0},
            ],
        }
    },
    test_data={"expected": "FAIL", "host": "R2", "destination": IP_4, "max_drop": 1},
)

ping_r3 = SelfTestData(
    name="r3",
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 3,
            "rtt_min": 1.0,
            "rtt_max": 2.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
                {"ip_address": IP_5, "rtt": 0.0},
            ],
        }
    },
    test_data={
        "expected": "FLAPPING",
        "host": "R3",
        "destination": IP_5,
        "max_drop": 1,
    },
)


@pytest.fixture
def general_result():
    task_name = "napalm_ping"
    confirmation_result = create_result(result_content="All pings executed")
    timeouted = create_result(
        TIMEOUT_MESSAGE,
        host="R3",
        destination=IP_6,
        failed=True,
        exception=ConnectionException(f"Cannot connect to {IP_6}"),
    )
    general_result = AggregatedResult(task_name)
    general_result["R1"] = create_multi_result(
        results=[
            confirmation_result,
            ping_r1_1.create_nornir_result(),
            ping_r1_2.create_nornir_result(),
        ],
        task_name=task_name,
    )
    general_result["R2"] = create_multi_result(
        results=[confirmation_result, ping_r2.create_nornir_result()],
        task_name=task_name,
    )
    general_result["R3"] = create_multi_result(
        results=[confirmation_result, ping_r3.create_nornir_result(), timeouted],
        task_name=task_name,
    )
    return general_result


@pytest.fixture(
    params=[ping_r1_1, ping_r1_2, ping_r2, ping_r3],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


pytestmark = [
    pytest.mark.nuts_test_ctx(
        CONTEXT(
            nuts_parameters={
                "test_data": [
                    ping_r1_1.test_data,
                    ping_r1_2.test_data,
                    ping_r2.test_data,
                    ping_r3.test_data,
                ]
            }
        )
    )
]


def test_contains_host_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


def test_contains_pinged_destination(transformed_result, testdata):
    assert testdata["destination"] in transformed_result[testdata["host"]]


def test_destination_maps_to_enum(transformed_result, testdata):
    host = testdata["host"]
    destination = testdata["destination"]
    expected = testdata["expected"]

    dest_result = transformed_result[host][destination]
    dest_result.validate()
    assert dest_result.result.name == expected


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"][IP_6].failed
    assert transformed_result["R3"][IP_6].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmPing",
        task_module=tasks,
        task_name="napalm_ping",
        test_count=1,
    )
