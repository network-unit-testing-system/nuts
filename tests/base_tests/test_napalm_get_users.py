import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.napalm_get_users import CONTEXT

test_data = [
    {"host": "R1", "username": "arya", "password": "stark", "level": 11},
    {"host": "R1", "username": "bran", "password": "stark", "level": 15},
    {"host": "R2", "username": "jon", "password": "snow", "level": 5},
]

result_data = [
    {
        "users": {
            "arya": {"level": 11, "password": "stark", "sshkeys": []},
            "bran": {"level": 15, "password": "stark", "sshkeys": []},
        }
    },
    {"users": {"jon": {"level": 5, "password": "snow", "sshkeys": []}}},
]


@pytest.fixture
def general_result(timeouted_multiresult):
    result = AggregatedResult("napalm_get_facts")

    multi_result_r1 = MultiResult("napalm_get_facts")
    result_r1 = Result(host=None, name="napalm_get_facts")
    result_r1.result = result_data[0]
    multi_result_r1.append(result_r1)
    result["R1"] = multi_result_r1

    multi_result_r2 = MultiResult("napalm_get_facts")
    result_r2 = Result(host=None, name="napalm_get_facts")
    result_r2.result = result_data[1]
    multi_result_r2.append(result_r2)
    result["R2"] = multi_result_r2

    result["R3"] = timeouted_multiresult
    return result


def _tupelize_dict(dict_data):
    return [tuple(k.values()) for k in dict_data]


# apply mark at module-level: https://docs.pytest.org/en/stable/example/markers.html#marking-whole-classes-or-modules
pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2", "R3"])
    def test_contains_host_at_toplevel(self, transformed_result, host):
        assert host in transformed_result

    @pytest.mark.parametrize("host, username", [("R1", "arya"), ("R1", "bran")])
    def test_contains_multiple_usernames_per_host(self, transformed_result, host, username):
        assert username in transformed_result[host].result

    @pytest.mark.parametrize("host, username, password, level", _tupelize_dict(test_data))
    def test_username_has_corresponding_password(self, transformed_result, host, username, password, level):
        assert transformed_result[host].result[username]["password"] == password

    @pytest.mark.parametrize("host, username, password, level", _tupelize_dict(test_data))
    def test_username_has_matching_privilegelevel(self, transformed_result, host, username, password, level):
        assert transformed_result[host].result[username]["level"] == level

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None
