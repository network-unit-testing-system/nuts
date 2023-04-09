import pytest
from nornir.core.task import AggregatedResult
import nornir_netmiko

from nuts.base_tests.netmiko_cdp_neighbors import CONTEXT
from tests.utils import SelfTestData, create_multi_result, create_result

SOFTWARE_VERSION = (
    "Cisco IOS Software [Gibraltar], Virtual XE Software "
    "(X86_64_LINUX_IOSD-UNIVERSALK9-M),\
        Version 16.11.1a, RELEASE SOFTWARE (fc1)",
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
    name="r1_r2",
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
    name="r1_r3",
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
    name="r1_r4",
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "local_port": "GigabitEthernet2",
        "remote_host": "R4",
        "remote_port": "GigabitEthernet2",
        "management_ip": "172.16.14.4",
    },
)

r1_count = SelfTestData(
    name="r1_count",
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "neighbor_count": 3,
    },
)

r2_r3 = SelfTestData(
    name="r2_r3",
    nornir_raw_result=raw_nornir_result_r2,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet4",
        "remote_host": "R3",
        "remote_port": "GigabitEthernet3",
        "management_ip": "172.16.23.3",
    },
)

r2_r1 = SelfTestData(
    name="r2_r3",
    nornir_raw_result=raw_nornir_result_r2,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet2",
        "remote_host": "R1",
        "remote_port": "GigabitEthernet3",
        "management_ip": "172.16.12.1",
    },
)

r2_r5 = SelfTestData(
    name="r2_r3",
    nornir_raw_result=raw_nornir_result_r2,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet3",
        "remote_host": "R5",
        "remote_port": "GigabitEthernet2",
        "management_ip": "172.16.211.11",
    },
)

r2_count = SelfTestData(
    name="r2_count",
    nornir_raw_result=raw_nornir_result_r2,
    test_data={
        "host": "R2",
        "neighbor_count": 3,
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "netmiko_send_command"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        [create_result(raw_nornir_result_r1, task_name)], task_name
    )
    result["R2"] = create_multi_result(
        [create_result(raw_nornir_result_r2, task_name)], task_name
    )
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[
        r1_r2,
        r1_r3,
        r1_r4,
        r2_r3,
        r2_r1,
        r2_r5,
    ],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


@pytest.fixture(
    params=[
        r1_count,
        r2_count,
    ],
    ids=lambda data: data.name,
)
def selftestdata_count(request):
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
    transformed_result[host].validate()
    assert transformed_result[host].result.keys() == neighbors


def test_contains_information_about_neighbor(transformed_result, testdata):
    host = testdata["host"]
    remote_host = testdata["remote_host"]

    host_result = transformed_result[host]
    host_result.validate()
    details = host_result.result[remote_host]
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


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNetmikoCdpNeighbors",
        task_module=nornir_netmiko,
        task_name="netmiko_send_command",
        test_count=4,
    )


def test_integration_count(selftestdata_count, integration_tester):
    integration_tester(
        selftestdata_count,
        test_class="TestNetmikoCdpNeighborsCount",
        task_module=nornir_netmiko,
        task_name="netmiko_send_command",
        test_count=1,
    )
