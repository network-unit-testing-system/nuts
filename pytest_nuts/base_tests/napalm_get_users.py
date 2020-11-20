from collections import defaultdict

import pytest
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get


@pytest.fixture(scope="class")
def nuts_task():
    return napalm_get


@pytest.fixture(scope="class")
def nuts_arguments():
    return {"getters": ["users"]}


@pytest.fixture(scope="class")
def nornir_filter(hosts):
    return F(name__any=hosts)


@pytest.fixture(scope="class")
def hosts(nuts_parameters):
    return {entry["host"] for entry in nuts_parameters["test_data"]}


@pytest.fixture(scope="class")
def transformed_result(general_result):
    return transform_result(general_result)


class TestNapalmUsers:
    @pytest.mark.nuts("host,username")
    def test_username(self, transformed_result, host, username):
        assert username in transformed_result[host]

    @pytest.mark.nuts("host,username,password")
    def test_password(self, transformed_result, host, username, password):
        assert transformed_result[host][username]["password"] == password

    @pytest.mark.nuts("host,username,level")
    def test_privilege_level(self, transformed_result, host, username, level):
        assert transformed_result[host][username]["level"] == level


class TestNapalmOnlyDefinedUsersExist:
    @pytest.mark.nuts("host,usernames")
    def test_no_rogue_users(self, transformed_result, host, usernames):
        assert list(transformed_result[host].keys()) == usernames


def transform_result(general_result):
    return {host: _transform_single_result(result) for host, result in general_result.items()}


def _transform_single_result(single_result):
    return single_result[0].result["users"]
