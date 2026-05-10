"""Query BGP neighbors of a device or count them."""

from typing import Dict, Callable, List, Any, Tuple

import pytest
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_get

from nuts.context import NornirNutsContext
from nuts.helpers.result import AbstractHostResultExtractor, NutsResult


class BgpNeighborsExtractor(AbstractHostResultExtractor):
    def single_transform(
        self, single_result: MultiResult
    ) -> Dict[Tuple[str, str], Dict[str, NutsResult]]:
        test_exectuion = self._nuts_ctx.nuts_parameters.get("test_execution")
        if test_exectuion:
            vrf = test_exectuion.get("vrf", "global")
            if not vrf:
                vrf = "global"
        else:
            vrf = "global"

        neighbors = self._simple_extract(single_result)["bgp_neighbors"]
        if vrf not in neighbors:
            return {}
        scope = neighbors[vrf]
        router_id = scope["router_id"]
        return {
            peer: self._add_local_id(details, router_id)
            for peer, details in scope["peers"].items()
        }

    def _add_local_id(self, element: Dict[str, Any], router_id: str) -> Dict[str, Any]:
        element["local_id"] = router_id
        return element


class BgpNeighborsContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_get

    def nuts_arguments(self) -> Dict[str, List[str]]:
        # Overrides nuts_arguments.nuts_arguments
        # "test_execution" is not passed to the nuts_task
        return {"getters": ["bgp_neighbors"]}

    def nuts_extractor(self) -> BgpNeighborsExtractor:
        return BgpNeighborsExtractor(self)


CONTEXT = BgpNeighborsContext


class TestNapalmBgpNeighborsCount:
    @pytest.mark.nuts("neighbor_count")
    def test_neighbor_count(
        self, single_result: NutsResult, neighbor_count: int
    ) -> None:
        assert single_result.result is not None
        assert (
            len(single_result.result) == neighbor_count
        ), f"Expected {neighbor_count}; got {len(single_result.result)}"


class TestNapalmBgpNeighbors:
    @pytest.fixture
    def peer_result(self, single_result: NutsResult, peer: str) -> Dict[str, Any]:
        assert single_result.result is not None
        return single_result.result[peer]

    @pytest.mark.nuts("peer,local_as")
    def test_local_as(self, peer_result: Dict[str, Any], local_as: int) -> None:
        assert peer_result["local_as"] == local_as

    @pytest.mark.nuts("peer,local_id")
    def test_local_id(self, peer_result: Dict[str, Any], local_id: str) -> None:
        assert peer_result["local_id"] == local_id

    @pytest.mark.nuts("peer,remote_as")
    def test_remote_as(self, peer_result: Dict[str, Any], remote_as: int) -> None:
        assert peer_result["remote_as"] == remote_as

    @pytest.mark.nuts("peer,remote_id")
    def test_remote_id(self, peer_result: Dict[str, Any], remote_id: str) -> None:
        assert peer_result["remote_id"] == remote_id

    @pytest.mark.nuts("peer,is_enabled")
    def test_is_enabled(self, peer_result: Dict[str, Any], is_enabled: bool) -> None:
        assert peer_result["is_enabled"] == is_enabled

    @pytest.mark.nuts("peer,is_up")
    def test_is_up(self, peer_result: Dict[str, Any], is_up: bool) -> None:
        assert peer_result["is_up"] == is_up
