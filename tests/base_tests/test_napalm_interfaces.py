import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_interfaces import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData

nornir_raw_result_r1 = {
    "interfaces": {
        "GigabitEthernet1": {
            "is_enabled": True,
            "is_up": True,
            "description": "",
            "mac_address": "CA:CA:00:CE:DE:00",
            "last_flapped": -1.0,
            "mtu": 1500,
            "speed": 1000,
        },
        "GigabitEthernet2": {
            "is_enabled": False,
            "is_up": True,
            "description": "",
            "mac_address": "C0:FF:EE:BE:EF:00",
            "last_flapped": -1.0,
            "mtu": 1500,
            "speed": 1000,
        },
    },
}

nornir_raw_result_r2 = {
    "interfaces": {
        "Loopback0": {
            "is_enabled": True,
            "is_up": False,
            "description": "",
            "mac_address": "",
            "last_flapped": -1.0,
            "mtu": 1514,
            "speed": 8000,
        },
        "GigabitEthernet3": {
            "is_enabled": False,
            "is_up": False,
            "description": "",
            "mac_address": "BE:EF:DE:AD:BE:EF",
            "last_flapped": -1.0,
            "mtu": 1500,
            "speed": 1000,
        },
    }
}

interfaces_r1_1 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "name": "GigabitEthernet1",
    },
)

interfaces_r1_2 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "host": "R1",
        "name": "GigabitEthernet2",
    },
)

interfaces_r2_1 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "host": "R2",
        "name": "Loopback0",
    },
)

interfaces_r2_2 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "host": "R2",
        "name": "GigabitEthernet3",
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        [interfaces_r1_1.create_nornir_result(task_name), interfaces_r1_2.create_nornir_result(task_name)], task_name
    )
    result["R2"] = create_multi_result(
        [interfaces_r2_1.create_nornir_result(task_name), interfaces_r2_2.create_nornir_result(task_name)], task_name
    )
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(params=[interfaces_r1_1, interfaces_r1_2, interfaces_r2_1, interfaces_r2_2])
def raw_testdata(request):
    return request.param


@pytest.fixture
def testdata(raw_testdata):
    return raw_testdata.test_data


@pytest.fixture
def single_result(transformed_result, testdata):
    return transformed_result[testdata["host"]].result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


def test_contains_interface_names_at_second_level(single_result, testdata):
    assert testdata["name"] in single_result


def test_contains_information_about_interface(single_result, raw_testdata, testdata):
    if_name = testdata["name"]
    assert single_result[if_name] == raw_testdata.nornir_raw_result["interfaces"][if_name]


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None
