import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_get_vlans import CONTEXT

from tests.utils import create_multi_result, SelfTestData

# Check
# If normal combination works vlan_name, vlan_tag
# If normal combination fails wrong name, correct tag
# If normal combination fails correct name, wrong tag
# If tag only works
# If wrong tag fails
# If tag as int works
# If tag as string works
# if tag as int work with vlan_name

nornir_raw_result_s1 = {
    1: {
        "name": "default",
        "interfaces": ["GigabitEthernet0/0/1", "GigabitEthernet0/0/2"],
    },
    2: {"name": "vlan2", "interfaces": []},
}

vlans_s1_1 = SelfTestData(
    name="s1_1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "vlan_name": "default", "vlan_tag": "1"},
)

vlans_s1_2 = SelfTestData(
    name="s1_2",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "vlan_tag": "2"},
)

vlans_s2 = SelfTestData(
    name="s2",
    nornir_raw_result={2: {"name": "vlan2", "interfaces": []}},
    test_data={"host": "S2", "vlan_name": "default", "vlan_tag": "2"},
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get_facts"
    result = AggregatedResult(task_name)
    result["S1"] = create_multi_result(
        [vlans_s1_1.create_nornir_result(), vlans_s1_2.create_nornir_result()],
        task_name,
    )
    result["S2"] = create_multi_result([vlans_s2.create_nornir_result()], task_name)
    # result["S3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[vlans_s1_1, vlans_s1_2, vlans_s2],
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
    assert transformed_result.keys() == {"S1", "S2"}


@pytest.fixture
def single_result(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    return host_result.result


# def test_contains_multiple_usernames_per_host(single_result, testdata):
#     assert testdata["vlans"] in single_result


# def test_vlan_tag_has_corresponding_vlan_name(single_result, testdata):
#     print(single_result)
#     assert single_result[testdata["vlan_tag"]["name"]] == testdata["vlan_name"]


# def test_username_has_matching_privilegelevel(single_result, testdata):
#     assert single_result[testdata["username"]]["level"] == testdata["level"]


# def test_marks_as_failed_if_task_failed(transformed_result):
#     assert transformed_result["R3"].failed
#     assert transformed_result["R3"].exception is not None


# def test_integration(selftestdata, integration_tester):
#     integration_tester(
#         selftestdata,
#         test_class="TestNapalmUsers",
#         task_module=tasks,
#         task_name="napalm_get",
#         test_count=3,
#     )
