"""Query vrf of a device."""
from typing import Dict, Callable, List, Any, Text

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import AbstractHostResultExtractor


class VrfExtractor(AbstractHostResultExtractor):
    def single_transform(
        self, single_result: MultiResult
    ) -> Dict[Text, Dict[Any, Any]]:
        network_instances = self._simple_extract(single_result)["network_instances"]
        result = {}
        for entry in network_instances:
            result[entry] = {"name": entry, "interfaces": []}
            for item in network_instances[entry]["interfaces"]["interface"]:
                result[entry]["interfaces"].append(item)
        return result


class VrfContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["network_instances"]}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> VrfExtractor:
        return VrfExtractor(self)


CONTEXT = VrfContext


class TestNapalmVrf:
    @pytest.mark.nuts("name")
    def test_vrf_exists(self, single_result, name):
        assert name in single_result.result

    @pytest.mark.nuts("name,interfaces")
    def test_vrf_and_interfaces(self, single_result, name, interfaces):
        assert all(
            item in single_result.result[name]["interfaces"] for item in interfaces
        )
