"""Query config of a device."""
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
        assert (
            bool(
                single_result.result["config"]["startup"]
                == single_result.result["config"]["running"]
            )
            == startup_equals_running_config
        )
