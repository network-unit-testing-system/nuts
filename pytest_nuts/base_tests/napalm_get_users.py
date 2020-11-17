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
        return {entry["source"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return transform_result(general_result)

    @pytest.mark.nuts("host,username")
    def test_username(self, transformed_result, username):
        raise Exception

    @pytest.mark.nuts("host,username")
    def test_password(self, transformed_result, password):
        raise Exception

    @pytest.mark.nuts("host,username")
    def test_privilege_level(self, transformed_result, level):
        raise Exception


def transform_result(general_result):
    return {source: _transform_single_result(result) for source, result in general_result.items()}


def _transform_single_result(single_result):
    return single_result[0].result[0].result["users"]
