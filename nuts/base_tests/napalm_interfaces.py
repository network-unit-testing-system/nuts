"""Query interfaces and their information of a device."""
from typing import Dict, Callable, List

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.converters import InterfaceNameConverter
from nuts.helpers.result import nuts_result_wrapper, NutsResult


class InterfacesContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["interfaces"]}

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, NutsResult]:
        return {
            host: nuts_result_wrapper(result, self._transform_host_results) for host, result in general_result.items()
        }

    def _transform_host_results(self, single_result: MultiResult) -> dict:
        assert single_result[0].result is not None
        return single_result[0].result["interfaces"]


CONTEXT = InterfacesContext


@pytest.mark.usefixtures("check_nuts_result")
class TestInterfaces:  # always required fields: host, name
    @pytest.mark.nuts("host,name,is_enabled")
    def test_is_enabled(self, single_result, name, is_enabled):
        assert single_result.result[name]["is_enabled"] == is_enabled

    @pytest.mark.nuts("host,name,is_up")
    def test_is_up(self, single_result, name, is_up):
        assert single_result.result[name]["is_up"] == is_up

    @pytest.mark.nuts("host,name,mac_address")
    def test_mac_address(self, single_result, name, mac_address):
        assert single_result.result[name]["mac_address"] == mac_address

    @pytest.mark.nuts("host,name,mtu")
    def test_mtu(self, single_result, name, mtu):
        assert single_result.result[name]["mtu"] == mtu

    @pytest.mark.nuts("host,name,speed")
    def test_speed(self, single_result, name, speed):
        assert single_result.result[name]["speed"] == speed
