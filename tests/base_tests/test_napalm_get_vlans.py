import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

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
nornir_raw_result_s1_mixed = {
    "vlans": {
        "2": {"name": "vlan2", "interfaces": []},
        "1": {
            "name": "default",
            "interfaces": ["GigabitEthernet0/0/1", "GigabitEthernet0/0/2"],
        },
    }
}
nornir_raw_result_s1_vlan1 = {
    "vlans": {
        "1": {
            "name": "default",
            "interfaces": ["GigabitEthernet0/0/1", "GigabitEthernet0/0/2"],
        },
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
    test_data={"host": "S1", "vlan_name": "default", "vlan_tag": 1},
)

vlans_s1_2 = SelfTestData(
    name="s1_2",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "vlan_name": "vlan2", "vlan_tag": 2},
)

vlans_s2 = SelfTestData(
    name="s2",
    nornir_raw_result=nornir_raw_result_s2,
    test_data={"host": "S2", "vlan_name": "vlan2", "vlan_tag": 2},
)

vlans_s1_taglist = SelfTestData(
    name="s1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "vlan_tags": {1, 2}},
)

vlans_s1_taglist_mixed = SelfTestData(
    name="s1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "vlan_tags": {2, 1}},
)

vlans_s1_taglist_nornir_mixed = SelfTestData(
    name="s1",
    nornir_raw_result=nornir_raw_result_s1_mixed,
    test_data={"host": "S1", "vlan_tags": {1, 2}},
)

vlans_s2_taglist = SelfTestData(
    name="s2",
    nornir_raw_result=nornir_raw_result_s2,
    test_data={"host": "S2", "vlan_tags": {2}},
)

vlans_s1_1_interface = SelfTestData(
    name="s1",
    nornir_raw_result=nornir_raw_result_s1_vlan1,
    test_data={"host": "S1", "interface": "GigabitEthernet0/0/1", "vlan_tag": 1},
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
    result["S3"] = timeouted_multiresult
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


@pytest.fixture(
    params=[vlans_s1_taglist, vlans_s1_taglist_mixed, vlans_s2_taglist],
    ids=lambda data: data.name,
)
def selftestdata_taglist(request):
    return request.param


@pytest.fixture(
    params=[vlans_s1_1_interface],
    ids=lambda data: data.name,
)
def selftestdata_interface(request):
    return request.param


@pytest.fixture
def testdata_taglist(selftestdata_taglist):
    return selftestdata_taglist.test_data


@pytest.fixture
def testdata_interface(selftestdata_interface):
    return selftestdata_interface.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    print(transformed_result)
    assert transformed_result.keys() == {"S1", "S2", "S3"}


@pytest.fixture
def single_result(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    return host_result.result


def test_vlan_tag_exists(single_result, testdata):
    assert testdata["vlan_tag"] in single_result


def test_vlan_tag_has_corresponding_vlan_name(single_result, testdata):
    assert single_result[testdata["vlan_tag"]]["name"] == testdata["vlan_name"]


def test_result_key_is_int(single_result):
    # tests if the string results from nornir (key to results) are
    # correctly converted to int
    assert all([isinstance(key, int) for key in single_result.keys()])


@pytest.mark.parametrize("nonexisting_tag", [-1, 17, 4096])
def test_nonexisting_vlan_fails(single_result, nonexisting_tag):
    assert nonexisting_tag not in single_result


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["S3"].failed
    assert transformed_result["S3"].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmVlans",
        task_module=tasks,
        task_name="napalm_get",
        test_count=2,
    )


def test_integration_definedvlans(selftestdata_taglist, integration_tester):
    integration_tester(
        selftestdata_taglist,
        test_class="TestNapalmOnlyDefinedVlansExist",
        task_module=tasks,
        task_name="napalm_get",
        test_count=1,
    )


def test_integration_interface_in_vlan(selftestdata_interface, integration_tester):
    integration_tester(
        selftestdata_interface,
        test_class="TestNapalmInterfaceInVlan",
        task_module=tasks,
        task_name="napalm_get",
        test_count=1,
    )
