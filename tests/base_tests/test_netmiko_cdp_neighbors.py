import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from nuts.base_tests.netmiko_cdp_neighbors import CONTEXT
from tests.helpers.selftest_helpers import SelfTestData, create_multi_result, create_result

SOFTWARE_VERSION = (
    "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
)
CAPABILITIES = ("Router IGMP",)
PLATFORM = ("cisco CSR1000V",)

raw_nornir_result_r1 = [
    {
        "destination_host": "R2",
        "management_ip": "172.16.12.2",
        "platform": PLATFORM,
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet3",
        "software_version": SOFTWARE_VERSION,
        "capabilities": CAPABILITIES,
    },
    {
        "destination_host": "R3",
        "management_ip": "172.16.13.3",
        "platform": PLATFORM,
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet4",
        "software_version": SOFTWARE_VERSION,
        "capabilities": CAPABILITIES,
    },
    {
        "destination_host": "R4",
        "management_ip": "172.16.14.4",
        "platform": PLATFORM,
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet2",
        "software_version": SOFTWARE_VERSION,
        "capabilities": CAPABILITIES,
    },
]

raw_nornir_result_r2 = [
    {
        "destination_host": "R3",
        "management_ip": "172.16.23.3",
        "platform": PLATFORM,
        "remote_port": "GigabitEthernet3",
        "local_port": "GigabitEthernet4",
        "software_version": SOFTWARE_VERSION,
        "capabilities": CAPABILITIES,
    },
    {
        "destination_host": "R1",
        "management_ip": "172.16.12.1",
        "platform": PLATFORM,
        "remote_port": "GigabitEthernet3",
        "local_port": "GigabitEthernet2",
        "software_version": SOFTWARE_VERSION,
        "capabilities": CAPABILITIES,
    },
    {
        "destination_host": "R5",
        "management_ip": "172.16.211.11",
        "platform": PLATFORM,
        "remote_port": "GigabitEthernet2",
        "local_port": "GigabitEthernet3",
        "software_version": SOFTWARE_VERSION,
        "capabilities": CAPABILITIES,
    },
]


r1_r2 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "local_port": "GigabitEthernet3",
        "remote_host": "R2",
        "remote_port": "GigabitEthernet2",
        "management_ip": "172.16.12.2",
    },
)

r1_r3 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "local_port": "GigabitEthernet4",
        "remote_host": "R3",
        "remote_port": "GigabitEthernet2",
        "management_ip": "172.16.13.3",
    },
)

r1_r4 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "local_port": "GigabitEthernet2",
        "remote_host": "R4",
        "remote_port": "GigabitEthernet2",
        "management_ip": "172.16.14.4",
    },
)

r2_r3 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet4",
        "remote_host": "R3",
        "remote_port": "GigabitEthernet3",
        "management_ip": "172.16.23.3",
    },
)

r2_r1 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet2",
        "remote_host": "R1",
        "remote_port": "GigabitEthernet3",
        "management_ip": "172.16.12.1",
    },
)

r2_r5 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet3",
        "remote_host": "R5",
        "remote_port": "GigabitEthernet2",
        "management_ip": "172.16.211.11",
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "netmiko_send_command"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result([create_result(raw_nornir_result_r1, task_name)], task_name)
    result["R2"] = create_multi_result([create_result(raw_nornir_result_r2, task_name)], task_name)
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[
        pytest.param(r1_r2.test_data, id="r1_r2"),
        pytest.param(r1_r3.test_data, id="r1_r3"),
        pytest.param(r1_r4.test_data, id="r1_r4"),
        pytest.param(r2_r3.test_data, id="r2_r3"),
        pytest.param(r2_r1.test_data, id="r2_r1"),
        pytest.param(r2_r5.test_data, id="r2_r5"),
    ]
)
def testdata(request):
    return request.param


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_hosts_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


@pytest.mark.parametrize(
    "host, neighbors",
    [
        ("R1", {"R2", "R3", "R4"}),
        ("R2", {"R3", "R1", "R5"}),
    ],
)
def test_contains_neighbors_at_second_level(transformed_result, host, neighbors):
    assert transformed_result[host].result.keys() == neighbors


def test_contains_information_about_neighbor(transformed_result, testdata):
    print(testdata)
    host = testdata["host"]
    remote_host = testdata["remote_host"]
    details = transformed_result[host].result[remote_host]
    expected = {
        "destination_host": remote_host,
        "management_ip": testdata["management_ip"],
        "platform": PLATFORM,
        "remote_port": testdata["remote_port"],
        "local_port": testdata["local_port"],
        "software_version": SOFTWARE_VERSION,
        "capabilities": CAPABILITIES,
    }
    assert details == expected


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None
