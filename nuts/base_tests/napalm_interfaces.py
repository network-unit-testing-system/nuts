"""Query interfaces and their information of a device."""
from typing import Dict, Callable, List, Any

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import AbstractHostResultExtractor


class InterfacesExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        return self._simple_extract(single_result)["interfaces"]


class InterfacesContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["interfaces"]}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> InterfacesExtractor:
        return InterfacesExtractor(self)


CONTEXT = InterfacesContext


class TestNapalmInterfaces:
    @pytest.mark.nuts("name,is_enabled")
    def test_is_enabled(self, single_result, name, is_enabled):
        assert single_result.result[name]["is_enabled"] == is_enabled

    @pytest.mark.nuts("name,is_up")
    def test_is_up(self, single_result, name, is_up):
        assert single_result.result[name]["is_up"] == is_up

    @pytest.mark.nuts("name,mac_address")
    def test_mac_address(self, single_result, name, mac_address):
        assert single_result.result[name]["mac_address"] == mac_address

    @pytest.mark.nuts("name,mtu")
    def test_mtu(self, single_result, name, mtu):
        assert single_result.result[name]["mtu"] == mtu

    @pytest.mark.nuts("name,speed")
    def test_speed(self, single_result, name, speed):
        assert single_result.result[name]["speed"] == speed
