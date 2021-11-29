"""Query users of a device."""
from typing import Dict, Callable, List, Any

import pytest
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.result import AbstractHostResultExtractor, NutsResult


class UsersExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        return self._simple_extract(single_result)["users"]


class UsersContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["users"]}

    def nuts_extractor(self) -> UsersExtractor:
        return UsersExtractor(self)


CONTEXT = UsersContext


class TestNapalmUsers:
    @pytest.mark.nuts("username")
    def test_username(self, single_result: NutsResult, username: str) -> None:
        assert username in single_result.result

    @pytest.mark.nuts("username,password")
    def test_password(
        self, single_result: NutsResult, username: str, password: str
    ) -> None:
        assert single_result.result[username]["password"] == password

    @pytest.mark.nuts("username,level")
    def test_privilege_level(
        self, single_result: NutsResult, username: str, level: int
    ) -> None:
        assert single_result.result[username]["level"] == level


class TestNapalmOnlyDefinedUsersExist:
    @pytest.mark.nuts("usernames")
    def test_no_rogue_users(
        self, single_result: NutsResult, usernames: List[str]
    ) -> None:
        assert list(single_result.result) == usernames
