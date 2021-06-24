"""Query network instances of a device."""
from typing import Dict, List, Callable, Any

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import NutsResult, AbstractResultExtractor
from nuts.context import NornirNutsContext


class NetworkInstancesExtractor(AbstractResultExtractor):
    def transform_result(
        self, general_result: AggregatedResult
    ) -> Dict[str, NutsResult]:
        return self.map_host_to_nutsresult(general_result)

    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        assert single_result[0].result is not None
        task_result = single_result[0].result
        network_instances = task_result["network_instances"]
        return {
            instance: self._transform_single_network_instance(details)
            for instance, details in network_instances.items()
        }

    def _transform_single_network_instance(
        self, network_instance: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "route_distinguisher": network_instance["state"]["route_distinguisher"],
            "interfaces": list(network_instance["interfaces"]["interface"]),
        }


class NetworkInstancesContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["network_instances"]}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> NetworkInstancesExtractor:
        return NetworkInstancesExtractor(self)


CONTEXT = NetworkInstancesContext


class TestNapalmNetworkInstances:
    @pytest.mark.nuts("network_instance,interfaces")
    def test_network_instance_contains_interfaces(
        self, single_result, network_instance, interfaces
    ):
        assert single_result.result[network_instance]["interfaces"] == interfaces

    @pytest.mark.nuts("network_instance,route_distinguisher")
    def test_route_distinguisher(
        self, single_result, network_instance, route_distinguisher
    ):
        assert (
            single_result.result[network_instance]["route_distinguisher"]
            == route_distinguisher
        )
