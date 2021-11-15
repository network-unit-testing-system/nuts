import pytest
from nornir.core.task import AggregatedResult

# from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_get_vlans import CONTEXT

from tests.utils import create_multi_result, SelfTestData

nornir_raw_result_s1 = {
    "vlans": {
        "1": {
            "name": "default",
            "interfaces": ["GigabitEthernet0/0/1", "GigabitEthernet0/0/2"],
        },
        "2": {"name": "vlan2", "interfaces": []},
    }
}
nornir_raw_result_s2 = {
    "vlans": {
        "2": {"name": "vlan2", "interfaces": []},
    }
}

vlans_s1_1 = SelfTestData(
    name="s1_1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "vlan_tags": {1, 2}},
)

vlans_s2 = SelfTestData(
    name="s2",
    nornir_raw_result=nornir_raw_result_s2,
    test_data={"host": "S2", "vlan_tags": {2}},
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get_facts"
    result = AggregatedResult(task_name)
    result["S1"] = create_multi_result(
        [vlans_s1_1.create_nornir_result()],
        task_name,
    )
    result["S2"] = create_multi_result([vlans_s2.create_nornir_result()], task_name)
    return result


@pytest.fixture(
    params=[vlans_s1_1, vlans_s2],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"S1", "S2"}


@pytest.fixture
def single_result(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    return host_result.result


def test_host_contains_all_vlans(single_result, testdata):
    assert list(single_result.keys()) == sorted(testdata["vlan_tags"])


# NOT WORKING YET
# def test_integration(selftestdata, integration_tester):
#   integration_tester(
#       selftestdata,
#       test_class="TestNapalmOnlyDefinedVlansExist",
#       task_module=tasks,
#       task_name="napalm_get",
#       test_count=1,
#   )
