import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_get_vrf import CONTEXT

from tests.utils import create_multi_result, SelfTestData


nornir_raw_result_s1 = {
    "network_instances": {
        "default": {
            "name": "default",
            "type": "DEFAULT_INSTANCE",
            "state": {
                "route_distinguisher": ""
            },
            "interfaces": {
                "interface": {
                    "GigabitEthernet0/1": {},
                    "GigabitEthernet0/2": {},
                    "GigabitEthernet0/3": {},
                }
            },
        },
        "mgmt": {
            "name": "mgmt",
            "type": "L3VRF",
            "state": {
                "route_distinguisher": ""
            },
            "interfaces": {
                "interface": {
                    "GigabitEthernet0/0": {},
                }
            },
        },
    }
}
nornir_raw_result_s2 = {
    "network_instances": {
        "default": {
            "name": "default",
            "type": "DEFAULT_INSTANCE",
            "state": {
                "route_distinguisher": ""
            },
            "interfaces": {
                "interface": {
                    "GigabitEthernet0/1": {},
                    "GigabitEthernet0/2": {},
                    "GigabitEthernet0/3": {},
                    "Vlan1": {}
                }
            },
        },
    }
}

vrf_s1_1 = SelfTestData(
    name="s1_1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={
        "host": "S1",
        "name": "mgmt",
        "interfaces": ["GigabitEthernet0/0"]
    },
)

vrf_s1_2 = SelfTestData(
    name="s1_2",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={
        "host": "S1",
        "name": "default",
        "interfaces": ["GigabitEthernet0/1", "GigabitEthernet0/2"]
    },
)

vrf_s2 = SelfTestData(
    name="s2",
    nornir_raw_result=nornir_raw_result_s2,
    test_data={
        "host": "S2",
        "name": "default",
        "interfaces": ["GigabitEthernet0/1", "Vlan1"]
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get_facts"
    result = AggregatedResult(task_name)
    result["S1"] = create_multi_result(
        [vrf_s1_1.create_nornir_result(), vrf_s1_2.create_nornir_result()],
        task_name,
    )
    result["S2"] = create_multi_result([vrf_s2.create_nornir_result()], task_name)
    result["S3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[vrf_s1_1, vrf_s1_2, vrf_s2],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    print(transformed_result)
    assert transformed_result.keys() == {"S1", "S2", "S3"}


@pytest.fixture
def single_result(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    return host_result.result


def test_vrf_exists(single_result, testdata):
    assert testdata["name"] in single_result


def test_vrf_and_interfaces(single_result, testdata):
    assert all(item in single_result[testdata["name"]]["interfaces"] for item in testdata["interfaces"])


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["S3"].failed
    assert transformed_result["S3"].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmVrf",
        task_module=tasks,
        task_name="napalm_get",
        test_count=2,
    )
