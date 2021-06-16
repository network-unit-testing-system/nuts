import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_get_users import CONTEXT

from tests.utils import create_multi_result, SelfTestData


nornir_raw_result_r1 = {
    "users": {
        "arya": {"level": 11, "password": "stark", "sshkeys": []},
        "bran": {"level": 15, "password": "stark", "sshkeys": []},
    }
}

users_r1_1 = SelfTestData(
    name="r1_1",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "username": "arya", "password": "stark", "level": 11},
)

users_r1_2 = SelfTestData(
    name="r1_2",
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "username": "bran", "password": "stark", "level": 15},
)

users_r2 = SelfTestData(
    name="r2",
    nornir_raw_result={
        "users": {"jon": {"level": 5, "password": "snow", "sshkeys": []}}
    },
    test_data={"host": "R2", "username": "jon", "password": "snow", "level": 5},
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get_facts"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        [users_r1_1.create_nornir_result(), users_r1_2.create_nornir_result()],
        task_name,
    )
    result["R2"] = create_multi_result([users_r2.create_nornir_result()], task_name)
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[users_r1_1, users_r1_2, users_r2],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_host_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


@pytest.fixture
def single_result(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    return host_result.result


def test_contains_multiple_usernames_per_host(single_result, testdata):
    assert testdata["username"] in single_result


def test_username_has_corresponding_password(single_result, testdata):
    assert single_result[testdata["username"]]["password"] == testdata["password"]


def test_username_has_matching_privilegelevel(single_result, testdata):
    assert single_result[testdata["username"]]["level"] == testdata["level"]


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmUsers",
        task_module=tasks,
        task_name="napalm_get",
        test_count=3,
    )
