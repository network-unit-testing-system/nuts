"""Query users of a device."""
from typing import Dict, Callable, List

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.result import nuts_result_wrapper, NutsResult


class UsersContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["users"]}

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, NutsResult]:
        return {
            host: nuts_result_wrapper(result, self._transform_host_results) for host, result in general_result.items()
        }

    def _transform_host_results(self, single_result: MultiResult) -> Dict[str, Dict]:
        assert single_result[0].result is not None
        return single_result[0].result["users"]


CONTEXT = UsersContext


@pytest.mark.usefixtures("check_nuts_result")
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
