from typing import Dict

import pytest
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult
from pytest_nuts.context import NornirNutsContext


class NetworkInstancesContext(NornirNutsContext):
    def nuts_task(self):
        return napalm_get

    def nuts_arguments(self):
        return {"getters": ["network_instances"]}

    def nornir_filter(self):
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def transform_result(self, general_result) -> Dict[str, NutsResult]:
        return {
            host: nuts_result_wrapper(result, self._transform_single_result) for host, result in general_result.items()
        }

    def _transform_single_result(self, single_result):
        task_result = single_result[0].result
        network_instances = task_result["network_instances"]
        return {
            instance: self._transform_single_network_instance(details)
            for instance, details in network_instances.items()
        }

    def _transform_single_network_instance(self, network_instance):
        return {
            "route_distinguisher": self._extract_route_distinguisher(network_instance),
            "interfaces": self._extract_interfaces(network_instance),
        }

    def _extract_route_distinguisher(self, element):
        return element["state"]["route_distinguisher"]

    def _extract_interfaces(self, element):
        return list(element["interfaces"]["interface"].keys())


CONTEXT = NetworkInstancesContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNapalmNetworkInstances:
    @pytest.mark.nuts("host,network_instance,interfaces")
    def test_network_instance_contains_interfaces(self, single_result, network_instance, interfaces):
        assert single_result.result[network_instance]["interfaces"] == interfaces

    @pytest.mark.nuts("host,network_instance,route_distinguisher")
    def test_route_distinguisher(self, single_result, network_instance, route_distinguisher):
        assert single_result.result[network_instance]["route_distinguisher"] == route_distinguisher
