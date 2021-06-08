import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_lldp_neighbors import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData

R1_CHASSIS_ID = "001e.e547.df00"
R2_CHASSIS_ID = "001e.f62f.a600"
R3_CHASSIS_ID = "001e.e611.3500"
REMOTE_SYSTEM_DESCRIPTION = "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
REMOTE_SYSTEM_CAPAB = ["bridge", "router"]
REMOTE_SYSTEM_ENABLE_CAPAB = ["router"]

nornir_raw_result_r1 = {
    "lldp_neighbors_detail": {
        "GigabitEthernet4": [
            {
                "remote_chassis_id": R3_CHASSIS_ID,
                "remote_port": "Gi2",
                "remote_port_description": "GigabitEthernet2",
                "remote_system_name": "R3",
                "remote_system_description": REMOTE_SYSTEM_DESCRIPTION,
                "remote_system_capab": REMOTE_SYSTEM_CAPAB,
                "remote_system_enable_capab": REMOTE_SYSTEM_ENABLE_CAPAB,
                "parent_interface": "",
            }
        ],
        "GigabitEthernet3": [
            {
                "remote_chassis_id": R2_CHASSIS_ID,
                "remote_port": "Gi2",
                "remote_port_description": "GigabitEthernet2",
                "remote_system_name": "R2",
                "remote_system_description": REMOTE_SYSTEM_DESCRIPTION,
                "remote_system_capab": REMOTE_SYSTEM_CAPAB,
                "remote_system_enable_capab": REMOTE_SYSTEM_ENABLE_CAPAB,
                "parent_interface": "",
            }
        ],
    }
}

nornir_raw_result_r2 = {
    "lldp_neighbors_detail": {
        "GigabitEthernet4": [
            {
                "remote_chassis_id": R3_CHASSIS_ID,
                "remote_port": "Gi3",
                "remote_port_description": "GigabitEthernet3",
                "remote_system_name": "R3",
                "remote_system_description": REMOTE_SYSTEM_DESCRIPTION,
                "remote_system_capab": REMOTE_SYSTEM_CAPAB,
                "remote_system_enable_capab": REMOTE_SYSTEM_ENABLE_CAPAB,
                "parent_interface": "",
            }
        ],
        "GigabitEthernet2": [
            {
                "remote_chassis_id": R1_CHASSIS_ID,
                "remote_port": "Gi3",
                "remote_port_description": "GigabitEthernet3",
                "remote_system_name": "R1",
                "remote_system_description": REMOTE_SYSTEM_DESCRIPTION,
                "remote_system_capab": REMOTE_SYSTEM_CAPAB,
                "remote_system_enable_capab": REMOTE_SYSTEM_ENABLE_CAPAB,
                "parent_interface": "",
            }
        ],
    }
}

lldp_r1_1 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "local_port": "GigabitEthernet4", "remote_host": "R3", "remote_port": "GigabitEthernet2"},
    additional_data={"remote_chassis_id": R3_CHASSIS_ID, "short_remote_port": "Gi2"},
)

lldp_r1_2 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "local_port": "GigabitEthernet3", "remote_host": "R2", "remote_port": "GigabitEthernet2"},
    additional_data={"remote_chassis_id": R2_CHASSIS_ID, "short_remote_port": "Gi2"},
)

lldp_r2_1 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r2,
    test_data={"host": "R2", "local_port": "GigabitEthernet4", "remote_host": "R3", "remote_port": "GigabitEthernet3"},
    additional_data={"remote_chassis_id": R3_CHASSIS_ID, "short_remote_port": "Gi3"},
)

lldp_r2_2 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r2,
    test_data={"host": "R2", "local_port": "GigabitEthernet2", "remote_host": "R1", "remote_port": "GigabitEthernet3"},
    additional_data={"remote_chassis_id": R1_CHASSIS_ID, "short_remote_port": "Gi3"},
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result([create_result(nornir_raw_result_r1, task_name)], task_name)
    result["R2"] = create_multi_result([create_result(nornir_raw_result_r2, task_name)], task_name)
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(params=[
    pytest.param(lldp_r1_1, id="r1_1"),
    pytest.param(lldp_r1_2, id="r1_2"),
    pytest.param(lldp_r2_1, id="r2_1"),
    pytest.param(lldp_r2_2, id="r2_2"),
])
def raw_testdata(request):
    return request.param


@pytest.fixture
def testdata(raw_testdata):
    return raw_testdata.test_data


@pytest.fixture
def interface_result(testdata, transformed_result):
    return transformed_result[testdata["host"]].result[testdata["local_port"]]


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_hosts_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


def test_contains_results_with_ports_at_second_level(transformed_result, testdata):
    assert testdata["local_port"] in transformed_result[testdata["host"]].result


def test_contains_failed_result_at_second_level_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception


def test_contains_information_about_neighbor(interface_result, testdata, raw_testdata):
    print(testdata)
    expected = {
        "remote_system_description": REMOTE_SYSTEM_DESCRIPTION,
        "remote_system_capab": REMOTE_SYSTEM_CAPAB,
        "remote_system_enable_capab": REMOTE_SYSTEM_ENABLE_CAPAB,
        "remote_chassis_id": raw_testdata.additional_data["remote_chassis_id"],
        "parent_interface": "",
        "remote_host": testdata["remote_host"],
        "remote_port": raw_testdata.additional_data["short_remote_port"],
        "remote_port_description": testdata["remote_port"],
        "remote_port_expanded": testdata["remote_port"],
        "remote_system_name": testdata["remote_host"],
    }
    assert interface_result == expected


def test_contains_information_remote_host(interface_result, testdata):
    assert interface_result["remote_host"] == testdata["remote_host"]


def test_contains_information_expanded_interface(interface_result, testdata):
    assert interface_result["remote_port_expanded"] == testdata["remote_port"]
