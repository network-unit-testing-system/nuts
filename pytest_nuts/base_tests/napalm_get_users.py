import pytest
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get


class TestNapalmUsers:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return napalm_get

    @pytest.fixture(scope="class")
    def nuts_arguments(self):
        return {"getters": ["users"]}

    @pytest.fixture(scope="class")
    def nornir_filter(self, hosts):
        return F(name__any=hosts)

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["host"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return transform_result(general_result)

    @pytest.mark.nuts("host,username")
    def test_username(self, transformed_result, host, username):
        assert username in transformed_result[host]

    @pytest.mark.nuts("host,username,password")
    def test_password(self,transformed_result, host, username, password):
        assert transformed_result[host][username]["password"] == password

    @pytest.mark.nuts("host,username,level")
    def test_privilege_level(self, transformed_result, host, username, level):
        assert transformed_result[host][username]["level"] == level


def transform_result(general_result):
    return {host: _transform_single_result(result) for host, result in general_result.items()}


def _transform_single_result(single_result):
    return single_result[0].result["users"]
