"""Query users of a device."""
from typing import Dict, Callable, List, Any

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import AbstractHostResultExtractor


class UsersExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        return self._simple_extract(single_result)["users"]


class UsersContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["users"]}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> UsersExtractor:
        return UsersExtractor(self)


CONTEXT = UsersContext


class TestNapalmUsers:
    @pytest.mark.nuts("username")
    def test_username(self, single_result, username):
        assert username in single_result.result

    @pytest.mark.nuts("username,password")
    def test_password(self, single_result, username, password):
        assert single_result.result[username]["password"] == password

    @pytest.mark.nuts("username,level")
    def test_privilege_level(self, single_result, username, level):
        assert single_result.result[username]["level"] == level


class TestNapalmOnlyDefinedUsersExist:
    @pytest.mark.nuts("usernames")
    def test_no_rogue_users(self, single_result, usernames):
        assert list(single_result.result) == usernames
