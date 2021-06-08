import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_network_instances import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData

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
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "network_instance": "mgmt",
        "interfaces": ["GigabitEthernet1"],
        "route_distinguisher": "",
    },
)


r1_space = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "network_instance": "space",
        "interfaces": [],
        "route_distinguisher": "",
    },
)


r1_ship = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "network_instance": "ship",
        "interfaces": ["Loopback2"],
        "route_distinguisher": "1:1",
    },
)


r2_default = SelfTestData(
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


r2_mgmt = SelfTestData(
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
    result["R1"] = create_multi_result([create_result(nornir_raw_result_r1, task_name)], task_name)
    result["R2"] = create_multi_result([create_result(nornir_raw_result_r2, task_name)], task_name)
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[
        pytest.param(r1_default.test_data, id="r1_default"),
        pytest.param(r1_mgmt.test_data, id="r1_mgmt"),
        pytest.param(r1_space.test_data, id="r1_space"),
        pytest.param(r1_ship.test_data, id="r1_ship"),
        pytest.param(r2_default.test_data, id="r2_default"),
        pytest.param(r2_mgmt.test_data, id="r2_mgmt"),
    ]
)
def testdata(request):
    return request.param


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
def test_contains_network_instances_at_second_level(transformed_result, host, network_instances):
    assert transformed_result[host].result.keys() == network_instances


def test_contains_interfaces_at_network_instance(transformed_result, testdata):
    host = testdata["host"]
    network_instance = testdata["network_instance"]
    expected = testdata["interfaces"]
    assert transformed_result[host].result[network_instance]["interfaces"] == expected


def test_contains_route_distinguisher_at_network_instance(transformed_result, testdata):
    host = testdata["host"]
    network_instance = testdata["network_instance"]
    expected = testdata["route_distinguisher"]
    assert transformed_result[host].result[network_instance]["route_distinguisher"] == expected


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None
