"""Query interfaces and their information of a device."""
from typing import Dict, Callable, List, Any

import pytest
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.result import AbstractHostResultExtractor, NutsResult


class InterfacesExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        return self._simple_extract(single_result)["interfaces"]


class InterfacesContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["interfaces"]}

    def nuts_extractor(self) -> InterfacesExtractor:
        return InterfacesExtractor(self)


CONTEXT = InterfacesContext


class TestNapalmInterfaces:
    @pytest.mark.nuts("name,is_enabled")
    def test_is_enabled(
        self, single_result: NutsResult, name: str, is_enabled: bool
    ) -> None:
        assert single_result.result[name]["is_enabled"] == is_enabled

    @pytest.mark.nuts("name,is_up")
    def test_is_up(self, single_result: NutsResult, name: str, is_up: bool) -> None:
        assert single_result.result[name]["is_up"] == is_up

    @pytest.mark.nuts("name,mac_address")
    def test_mac_address(
        self, single_result: NutsResult, name: str, mac_address: str
    ) -> None:
        assert single_result.result[name]["mac_address"] == mac_address

    @pytest.mark.nuts("name,mtu")
    def test_mtu(self, single_result: NutsResult, name: str, mtu: int) -> None:
        assert single_result.result[name]["mtu"] == mtu

    @pytest.mark.nuts("name,speed")
    def test_speed(self, single_result: NutsResult, name: str, speed: int) -> None:
        assert single_result.result[name]["speed"] == speed
