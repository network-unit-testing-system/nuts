"""Query config of a device."""

import re
from typing import Dict, Callable, List, Any

import pytest
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.result import AbstractHostResultExtractor


class ConfigExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[int, Any]:
        return self._simple_extract(single_result)


class ConfigContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["config"]}

    def nuts_extractor(self) -> ConfigExtractor:
        return ConfigExtractor(self)


CONTEXT = ConfigContext


class TestNapalmConfig:
    @pytest.mark.nuts("startup_equals_running_config")
    def test_startup_equals_running_config(
        self, single_result, startup_equals_running_config
    ):
        pattern = (
            r"! Command: show (startup|running)-config\n"
            r"(! Startup-config last modified at .* by .*\n)?"
        )
        startup = re.sub(pattern, "", single_result.result["config"]["startup"])
        running = re.sub(pattern, "", single_result.result["config"]["running"])
        assert bool(startup == running) == startup_equals_running_config
