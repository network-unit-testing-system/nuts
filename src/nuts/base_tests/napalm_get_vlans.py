"""Query vlans of a device."""

from typing import Dict, Callable, List, Any

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import AbstractHostResultExtractor


class VlansExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[int, Any]:
        return self._cast_to_int(self._simple_extract(single_result)["vlans"])

    def _cast_to_int(self, elements: Dict[str, Any]) -> Dict[int, Any]:
        return {int(key): elements[key] for key in elements}


class VlansContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["vlans"]}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> VlansExtractor:
        return VlansExtractor(self)


CONTEXT = VlansContext


class TestNapalmVlans:
    @pytest.mark.nuts("vlan_tag")
    def test_vlan_tag(self, single_result, vlan_tag):
        assert vlan_tag in single_result.result

    @pytest.mark.nuts("vlan_name,vlan_tag")
    def test_vlan_name_to_tag(self, single_result, vlan_name, vlan_tag):
        assert single_result.result[vlan_tag]["name"] == vlan_name


class TestNapalmOnlyDefinedVlansExist:
    @pytest.mark.nuts("vlan_tags")
    def test_no_rogue_vlans(self, single_result, vlan_tags):
        assert sorted(list(single_result.result.keys())) == sorted(vlan_tags)


class TestNapalmInterfaceInVlan:
    @pytest.mark.nuts("vlan_tag,interface")
    def test_interface_port(self, single_result, vlan_tag, interface):
        assert interface in single_result.result[vlan_tag]["interfaces"]
