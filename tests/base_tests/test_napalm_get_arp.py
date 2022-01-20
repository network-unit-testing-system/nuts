import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_get_arp import CONTEXT

from tests.utils import create_multi_result, SelfTestData


nornir_raw_result_s1 = {
    "arp_table": [
        {
            "interface": "Vlan1",
            "mac": "52:54:00:74:9B:D2",
            "ip": "10.0.0.30",
            "age": 144.0,
        },
        {
            "interface": "Vlan200",
            "mac": "00:00:0C:9F:F0:C8",
            "ip": "10.0.200.1",
            "age": 230.0,
        },
    ]
}
nornir_raw_result_s2 = {
    "arp_table": [
        {
            "interface": "Vlan1",
            "mac": "52:54:00:54:92:C3",
            "ip": "10.0.0.50",
            "age": 144.0,
        }
    ]
}

arp_s1_1 = SelfTestData(
    name="s1_1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "interface": "Vlan1", "ip": "10.0.0.30"},
)

arp_s1_2 = SelfTestData(
    name="s1_2",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "interface": "Vlan200", "ip": "10.0.200.1"},
)

arp_s1 = SelfTestData(
    name="s2",
    nornir_raw_result=nornir_raw_result_s2,
    test_data={"host": "S2", "interface": "Vlan1", "ip": "10.0.0.50"},
)

arp_s1_range = SelfTestData(
    name="s1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "min": 2, "max": 4},
)

arp_s2_range = SelfTestData(
    name="s2",
    nornir_raw_result=nornir_raw_result_s2,
    test_data={"host": "S2", "min": 0, "max": 2},
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get_facts"
    result = AggregatedResult(task_name)
    result["S1"] = create_multi_result(
        [arp_s1_1.create_nornir_result(), arp_s1_2.create_nornir_result()],
        task_name,
    )
    result["S2"] = create_multi_result([arp_s1.create_nornir_result()], task_name)
    result["S3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[arp_s1_1, arp_s1_2, arp_s1],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


@pytest.fixture(
    params=[arp_s1_range, arp_s2_range],
    ids=lambda data: data.name,
)
def selftestdata_range(request):
    return request.param


@pytest.fixture
def testdata_taglist(selftestdata_range):
    return selftestdata_range.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    print(transformed_result)
    assert transformed_result.keys() == {"S1", "S2", "S3"}


@pytest.fixture
def single_result(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    return host_result.result


def test_arp_entry(single_result, testdata):
    assert {"interface": testdata["interface"], "ip": testdata["ip"]} in single_result


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["S3"].failed
    assert transformed_result["S3"].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmArp",
        task_module=tasks,
        task_name="napalm_get",
        test_count=1,
    )


def test_integration_range(selftestdata_range, integration_tester):
    integration_tester(
        selftestdata_range,
        test_class="TestNapalmArpRange",
        task_module=tasks,
        task_name="napalm_get",
        test_count=1,
    )
