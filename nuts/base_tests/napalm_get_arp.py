"""Query vlans of a device."""
from typing import Dict, Callable, List, Any, Text

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import AbstractHostResultExtractor


class ArpExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> List[Dict[Text, Any]]:
        result = []
        for entry in self._simple_extract(single_result)['arp_table']:
            result.append({'interface': entry['interface'], 'ip': entry['ip']})
        return result


class ArpContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["arp_table"]}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> ArpExtractor:
        return ArpExtractor(self)


CONTEXT = ArpContext


class TestNapalmArp:
    @pytest.mark.nuts("interface,ip")
    def test_arp_entry(self, single_result, interface, ip):
        assert {'interface': interface, 'ip': ip} in single_result.result


class TestNapalmArpRange:
    @pytest.mark.nuts("min,max")
    def test_amount_of_arp_entries(self, single_result, min, max):
        assert min <= len(single_result.result) <= max
