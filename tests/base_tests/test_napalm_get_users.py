import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from nuts.base_tests.napalm_get_users import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData, tupelize

nornir_raw_result_r1 = {
        "users": {
            "arya": {"level": 11, "password": "stark", "sshkeys": []},
            "bran": {"level": 15, "password": "stark", "sshkeys": []},
        }
    }

users_r1_1 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "username": "arya", "password": "stark", "level": 11},
)

users_r1_2 = SelfTestData(
    nornir_raw_result=nornir_raw_result_r1,
    test_data={"host": "R1", "username": "bran", "password": "stark", "level": 15},
)

users_r2 = SelfTestData(
    nornir_raw_result={"users": {"jon": {"level": 5, "password": "snow", "sshkeys": []}}},
    test_data={"host": "R2", "username": "jon", "password": "snow", "level": 5},
)

@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get_facts"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result([users_r1_1.create_nornir_result(task_name), users_r1_2.create_nornir_result(task_name)], task_name)
    result["R2"] = create_multi_result([users_r2.create_nornir_result(task_name)], task_name)
    result["R3"] = timeouted_multiresult
    return result

pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2", "R3"])
    def test_contains_host_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    def test_contains_multiple_usernames_per_host(self, transformed_result):
        expected_r1_users = [users_r1_1.test_data["username"], users_r1_2.test_data["username"]]
        assert all(u in transformed_result["R1"].result for u in expected_r1_users)

    def test_username_has_corresponding_password(self, transformed_result):
        expected = [users_r1_1.test_data, users_r1_2.test_data, users_r2.test_data]
        for entry in expected:
            assert transformed_result[entry["host"]].result[entry["username"]]["password"] == entry["password"]

    def test_username_has_matching_privilegelevel(self, transformed_result):
        expected = [users_r1_1.test_data, users_r1_2.test_data, users_r2.test_data]
        for entry in expected:
            assert transformed_result[entry["host"]].result[entry["username"]]["level"] == entry["level"]

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
