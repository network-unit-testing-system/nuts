"""Query interfaces and their information of a device."""
from typing import Dict, Callable, List

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult
from nornir_napalm.plugins.tasks import napalm_get

from pytest_nuts.context import NornirNutsContext
from pytest_nuts.helpers.converters import InterfaceNameConverter
from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult

from nornir_napalm.plugins.tasks import napalm_get

# TODO not implemented

class InterfacesContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List]:
        return {"getters": ["interfaces"]}

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def transform_result(self, general_result) -> Dict[str, NutsResult]:
        return {
            host: nuts_result_wrapper(result, self._transform_host_results) for host, result in general_result.items()
        }

CONTEXT = InterfacesContext

@pytest.mark.usefixtures("check_nuts_result")
class TestInterfaces:
    pass