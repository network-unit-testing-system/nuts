from typing import Dict, Callable, Set

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, AggregatedResult, Result
from nornir_napalm.plugins.tasks import napalm_get
from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult


@pytest.fixture(scope="class")
def nuts_task() -> Callable:
    return napalm_get


@pytest.fixture(scope="class")
def nuts_arguments() -> Dict:
    return {"getters": ["bgp_neighbors"]}


@pytest.fixture(scope="class")
def nornir_filter(hosts: Set) -> F:
    return F(name__any=hosts)


@pytest.fixture(scope="class")
def hosts(nuts_parameters: Dict):
    return {entry["host"] for entry in nuts_parameters["test_data"]}


@pytest.fixture(scope="class")
def transformed_result(general_result: AggregatedResult):
    return transform_result(general_result)


@pytest.mark.usefixtures("check_nuts_result")
class TestNapalmBgpNeighborsCount:
    @pytest.fixture
    def single_result(self, transformed_result, host):
        assert host in transformed_result, f"Host {host} not found in aggregated result."
        return transformed_result[host]

    @pytest.mark.nuts("host,neighbor_count")
    def test_neighbor_count(self, single_result, neighbor_count):
        assert len(single_result.result) == neighbor_count


@pytest.mark.usefixtures("check_nuts_result")
class TestNapalmBgpNeighbors:
    @pytest.fixture
    def single_result(self, transformed_result: Dict, host: str):
        assert host in transformed_result, f"Host {host} not found in aggregated result."
        return transformed_result[host]

    @pytest.fixture
    def peer_result(self, single_result: NutsResult, peer: str):
        return single_result.result[peer]

    @pytest.mark.nuts("host,peer,local_as")
    def test_local_as(self, peer_result: Dict, local_as: int):
        assert peer_result["local_as"] == local_as

    @pytest.mark.nuts("host,peer,local_id")
    def test_local_id(self, peer_result: Dict, local_id: str):
        assert peer_result["local_id"] == local_id

    @pytest.mark.nuts("host,peer,remote_as")
    def test_remote_as(self, peer_result: Dict, remote_as: int):
        assert peer_result["remote_as"] == remote_as

    @pytest.mark.nuts("host,peer,remote_id")
    def test_remote_id(self, peer_result: Dict, remote_id: str):
        assert peer_result["remote_id"] == remote_id

    @pytest.mark.nuts("host,peer,is_enabled")
    def test_is_enabled(self, peer_result: Dict, is_enabled: bool):
        assert peer_result["is_enabled"] == is_enabled

    @pytest.mark.nuts("host,peer,is_up")
    def test_is_up(self, peer_result: Dict, is_up: bool):
        assert peer_result["is_up"] == is_up


def transform_result(general_result: AggregatedResult) -> Dict[str, NutsResult]:
    return {host: nuts_result_wrapper(result, _transform_single_result) for host, result in general_result.items()}


def _transform_single_result(single_result: MultiResult) -> Dict:
    task_result = single_result[0].result
    neighbors = task_result["bgp_neighbors"]
    if "global" not in neighbors:
        return {}
    global_scope = neighbors["global"]
    router_id = global_scope["router_id"]
    return {peer: _add_local_id(details, router_id) for peer, details in global_scope["peers"].items()}


def _add_local_id(element: Dict, router_id: str) -> Dict:
    element["local_id"] = router_id
    return element
