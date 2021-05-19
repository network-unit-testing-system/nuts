"""Query BGP neighbors of a device or count them."""
from typing import Dict, Callable, List, Any, Sized

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult, Result, Task
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_get import GetterOptionsDict

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import map_host_to_nutsresult, NutsResult


class BgpNeighborsContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"getters": ["bgp_neighbors"]}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, NutsResult]:
        return map_host_to_nutsresult(general_result, self._transform_host_results)

    def _transform_host_results(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        assert single_result[0].result is not None
        task_result = single_result[0].result
        neighbors = task_result["bgp_neighbors"]
        if "global" not in neighbors:
            return {}
        global_scope = neighbors["global"]
        router_id = global_scope["router_id"]
        return {peer: self._add_local_id(details, router_id) for peer, details in global_scope["peers"].items()}

    def _add_local_id(self, element: Dict[str, Any], router_id: str) -> Dict[str, Any]:
        element["local_id"] = router_id
        return element


CONTEXT = BgpNeighborsContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNapalmBgpNeighborsCount:
    @pytest.mark.nuts("host,neighbor_count")
    def test_neighbor_count(self, single_result: NutsResult, neighbor_count: int) -> None:
        assert single_result.result is not None
        assert len(single_result.result) == neighbor_count


@pytest.mark.usefixtures("check_nuts_result")
class TestNapalmBgpNeighbors:
    @pytest.fixture
    def peer_result(self, single_result: NutsResult, peer: str) -> Dict[str, Any]:
        assert single_result.result is not None
        return single_result.result[peer]

    @pytest.mark.nuts("host,peer,local_as")
    def test_local_as(self, peer_result: Dict[str, Any], local_as: int) -> None:
        assert peer_result["local_as"] == local_as

    @pytest.mark.nuts("host,peer,local_id")
    def test_local_id(self, peer_result: Dict[str, Any], local_id: str) -> None:
        assert peer_result["local_id"] == local_id

    @pytest.mark.nuts("host,peer,remote_as")
    def test_remote_as(self, peer_result: Dict[str, Any], remote_as: int) -> None:
        assert peer_result["remote_as"] == remote_as

    @pytest.mark.nuts("host,peer,remote_id")
    def test_remote_id(self, peer_result: Dict[str, Any], remote_id: str) -> None:
        assert peer_result["remote_id"] == remote_id

    @pytest.mark.nuts("host,peer,is_enabled")
    def test_is_enabled(self, peer_result: Dict[str, Any], is_enabled: bool) -> None:
        assert peer_result["is_enabled"] == is_enabled

    @pytest.mark.nuts("host,peer,is_up")
    def test_is_up(self, peer_result: Dict[str, Any], is_up: bool) -> None:
        assert peer_result["is_up"] == is_up
