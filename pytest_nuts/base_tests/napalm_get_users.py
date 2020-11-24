from collections import defaultdict
from typing import Dict

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult
from nornir_napalm.plugins.tasks import napalm_get

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult

# noinspection PyUnresolvedReferences
from pytest_nuts.helpers.result import check_result


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


@pytest.fixture
def single_result(transformed_result, host):
    assert host in transformed_result, f"Host {host} not found in aggregated result."
    return transformed_result[host]


@pytest.mark.usefixtures("check_result")
class TestNapalmUsers:
    @pytest.mark.nuts("host,username")
    def test_username(self, single_result, username):
        assert username in single_result.result

    @pytest.mark.nuts("host,username,password")
    def test_password(self, single_result, username, password):
        assert single_result.result[username]["password"] == password

    @pytest.mark.nuts("host,username,level")
    def test_privilege_level(self, single_result, username, level):
        assert single_result.result[username]["level"] == level


class TestNapalmOnlyDefinedUsersExist:
    @pytest.mark.nuts("host,usernames")
    def test_no_rogue_users(self, single_result, usernames):
        assert list(single_result.result.keys()) == usernames


def transform_result(general_result) -> Dict[str, NutsResult]:
    return {host: nuts_result_wrapper(result, _transform_single_result) for host, result in general_result.items()}


def _transform_single_result(single_result: MultiResult) -> dict:
    return single_result[0].result["users"]
