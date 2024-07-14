import copy
import re
import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_network_instances import CONTEXT
from tests.utils import create_multi_result, create_result, SelfTestData

nornir_raw_result_r1 = {
    "network_instances": {
        "default": {
            "name": "default",
            "type": "DEFAULT_INSTANCE",
            "state": {"route_distinguisher": ""},
            "interfaces": {
                "interface": {
                    "GigabitEthernet2": {},
                    "GigabitEthernet3": {},
                    "GigabitEthernet4": {},
                    "GigabitEthernet5": {},
                    "Loopback0": {},
                }
            },
        },
        "mgmt": {
            "name": "mgmt",
            "type": "L3VRF",
            "state": {"route_distinguisher": ""},
            "interfaces": {"interface": {"GigabitEthernet1": {}}},
        },
        "space": {
            "name": "space",
            "type": "L3VRF",
            "state": {"route_distinguisher": ""},
            "interfaces": {"interface": {}},
        },
        "ship": {
            "name": "ship",
            "type": "L3VRF",
            "state": {"route_distinguisher": "1:1"},
            "interfaces": {"interface": {"Loopback2": {}}},
        },
    }
}

nornir_raw_result_r2 = {
    "network_instances": {
        "default": {
            "name": "default",
            "type": "DEFAULT_INSTANCE",
            "state": {"route_distinguisher": ""},
            "interfaces": {
                "interface": {
                    "GigabitEthernet2": {},
                    "GigabitEthernet3": {},
                    "GigabitEthernet4": {},
                    "Loopback0": {},
                }
            },
        },
        "mgmt": {
            "name": "mgmt",
            "type": "L3VRF",
            "state": {"route_distinguisher": ""},
            "interfaces": {"interface": {"GigabitEthernet1": {}}},
        },
    }
}


r1_default = SelfTestData(
    name="r1_default",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "network_instance": "default",
        "interfaces": [
            "GigabitEthernet2",
            "GigabitEthernet3",
            "GigabitEthernet4",
            "GigabitEthernet5",
            "Loopback0",
        ],
        "route_distinguisher": "",
    },
)


r1_mgmt = SelfTestData(
    name="r1_mgmt",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "network_instance": "mgmt",
        "interfaces": ["GigabitEthernet1"],
        "route_distinguisher": "",
    },
)


r1_space = SelfTestData(
    name="r1_space",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "network_instance": "space",
        "interfaces": [],
        "route_distinguisher": "",
    },
)


r1_ship = SelfTestData(
    name="r1_ship",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "network_instance": "ship",
        "interfaces": ["Loopback2"],
        "route_distinguisher": "1:1",
    },
)


r2_default = SelfTestData(
    name="r2_default",
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "host": "R2",
        "network_instance": "default",
        "interfaces": [
            "GigabitEthernet2",
            "GigabitEthernet3",
            "GigabitEthernet4",
            "Loopback0",
        ],
        "route_distinguisher": "",
    },
)

r2_default_range = SelfTestData(
    name="r2_default",
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "host": "R2",
        "network_instance": "default",
        "interfaces": [
            "GigabitEthernet[2-4]",
            "Loopback0",
        ],
        "route_distinguisher": "",
    },
)

r2_default_digit = SelfTestData(
    name="r2_default",
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "host": "R2",
        "network_instance": "default",
        "interfaces": [
            "GigabitEthernet\\d{1}",
            "Loopback0",
        ],
        "route_distinguisher": "",
    },
)


r2_mgmt = SelfTestData(
    name="r2_mgmt",
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "host": "R2",
        "network_instance": "mgmt",
        "interfaces": ["GigabitEthernet1"],
        "route_distinguisher": "",
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        [create_result(nornir_raw_result_r1, task_name)], task_name
    )
    result["R2"] = create_multi_result(
        [create_result(nornir_raw_result_r2, task_name)], task_name
    )
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[
        r1_default,
        r1_mgmt,
        r1_space,
        r1_ship,
        r2_default,
        r2_default_range,
        r2_default_digit,
        r2_mgmt,
    ],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_hosts_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


@pytest.mark.parametrize(
    "host, network_instances",
    [
        ("R1", {"default", "mgmt", "space", "ship"}),
        ("R2", {"default", "mgmt"}),
    ],
)
def test_contains_network_instances_at_second_level(
    transformed_result, host, network_instances
):
    host_result = transformed_result[host]
    host_result.validate()
    assert host_result.result.keys() == network_instances


def test_contains_interfaces_at_network_instance(transformed_result, testdata):
    host = testdata["host"]
    network_instance = testdata["network_instance"]
    expected = testdata["interfaces"]

    host_result = transformed_result[host]
    host_result.validate()
    patterns = len(expected)
    matches = 0
    result = copy.deepcopy(host_result.result[network_instance]["interfaces"])
    for interface in expected:
        pattern = re.compile(interface)
        for i in result:
            if pattern.match(i):
                host_result.result[network_instance]["interfaces"].remove(i)
        if len(result) != len(host_result.result[network_instance]["interfaces"]):
            result = copy.deepcopy(host_result.result[network_instance]["interfaces"])
            matches += 1
    assert patterns == matches
    assert result == []
    # assert host_result.result[network_instance]["interfaces"] == expected


def test_contains_route_distinguisher_at_network_instance(transformed_result, testdata):
    host = testdata["host"]
    network_instance = testdata["network_instance"]
    expected = testdata["route_distinguisher"]

    host_result = transformed_result[host]
    host_result.validate()
    assert host_result.result[network_instance]["route_distinguisher"] == expected


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmNetworkInstances",
        task_module=tasks,
        task_name="napalm_get",
        test_count=3,
    )
