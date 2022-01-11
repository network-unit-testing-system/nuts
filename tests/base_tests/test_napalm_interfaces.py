import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_interfaces import CONTEXT
from tests.utils import create_multi_result, SelfTestData

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
    name="r1_1",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "is_enabled": True,
        "host": "R1",
        "name": "GigabitEthernet1",
        "is_up": True,
        "mac_address": "CA:CA:00:CE:DE:00",
        "speed": 1000,
        "mtu": 1500,
    },
)

interfaces_r1_2 = SelfTestData(
    name="r1_2",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={
        "is_enabled": False,
        "host": "R1",
        "name": "GigabitEthernet2",
        "is_up": True,
        "mac_address": "C0:FF:EE:BE:EF:00",
        "speed": 1000,
        "mtu": 1500,
    },
)

interfaces_r2_1 = SelfTestData(
    name="r2_1",
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "is_enabled": True,
        "host": "R2",
        "name": "Loopback0",
        "is_up": False,
        "mac_address": "",
        "speed": 8000,
        "mtu": 1514,
    },
)

interfaces_r2_2 = SelfTestData(
    name="r2_2",
    nornir_raw_result=nornir_raw_result_r2,
    test_data={
        "is_enabled": False,
        "host": "R2",
        "name": "GigabitEthernet3",
        "is_up": False,
        "mac_address": "BE:EF:DE:AD:BE:EF",
        "speed": 1000,
        "mtu": 1500,
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        [
            interfaces_r1_1.create_nornir_result(),
            interfaces_r1_2.create_nornir_result(),
        ],
        task_name,
    )
    result["R2"] = create_multi_result(
        [
            interfaces_r2_1.create_nornir_result(),
            interfaces_r2_2.create_nornir_result(),
        ],
        task_name,
    )
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[
        interfaces_r1_1,
        interfaces_r1_2,
        interfaces_r2_1,
        interfaces_r2_2,
    ],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


@pytest.fixture
def single_result(transformed_result, testdata):
    res = transformed_result[testdata["host"]]
    res.validate()
    return res.result


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


def test_contains_interface_names_at_second_level(single_result, testdata):
    assert testdata["name"] in single_result


def test_contains_information_about_interface(single_result, testdata):
    expected = {
        "is_enabled": testdata["is_enabled"],
        "is_up": testdata["is_up"],
        "mac_address": testdata["mac_address"],
        "mtu": testdata["mtu"],
        "speed": testdata["speed"],
        "description": "",
        "last_flapped": -1.0,
    }
    assert single_result[testdata["name"]] == expected


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmInterfaces",
        task_module=tasks,
        task_name="napalm_get",
        test_count=5,
    )
