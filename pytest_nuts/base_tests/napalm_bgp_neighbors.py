from typing import Dict

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult
from nornir_napalm.plugins.tasks import napalm_get
from pytest_nuts.helpers.result import nuts_result_wrapper, check_result, NutsResult


@pytest.fixture(scope="class")
def nuts_task():
    return napalm_get


@pytest.fixture(scope="class")
def nuts_arguments():
    return {"getters": ["bgp_neighbors"]}


@pytest.fixture(scope="class")
def nornir_filter(hosts):
    return F(name__any=hosts)


@pytest.fixture(scope="class")
def hosts(nuts_parameters):
    return {entry["source"] for entry in nuts_parameters["test_data"]}


@pytest.fixture(scope="class")
def transformed_result(general_result):
    return transform_result(general_result)


@pytest.mark.usefixtures("check_result")
class TestNapalmBgpNeighborsCount:
    @pytest.fixture
    def single_result(self, transformed_result, source):
        assert source in transformed_result, f"Host {source} not found in aggregated result."
        return transformed_result[source]

    @pytest.mark.nuts("source,neighbor_count")
    def test_neighbor_count(self, single_result, neighbor_count):
        assert len(single_result.result) == neighbor_count


@pytest.mark.usefixtures("check_result")
class TestNapalmBgpNeighbors:
    @pytest.fixture
    def single_result(self, transformed_result, source):
        assert source in transformed_result, f"Host {source} not found in aggregated result."
        return transformed_result[source]

    @pytest.fixture
    def peer_result(self, single_result, peer):
        return single_result.result[peer]

    @pytest.mark.nuts("source,peer,local_as")
    def test_local_as(self, peer_result, local_as):
        assert peer_result["local_as"] == local_as

    @pytest.mark.nuts("source,peer,local_id")
    def test_local_id(self, peer_result, local_id):
        assert peer_result["local_id"] == local_id

    @pytest.mark.nuts("source,peer,remote_as")
    def test_remote_as(self, peer_result, remote_as):
        assert peer_result["remote_as"] == remote_as

    @pytest.mark.nuts("source,peer,remote_id")
    def test_remote_id(self, peer_result, remote_id):
        assert peer_result["remote_id"] == remote_id

    @pytest.mark.nuts("source,peer,is_enabled")
    def test_is_enabled(self, peer_result, is_enabled):
        assert peer_result["is_enabled"] == is_enabled

    @pytest.mark.nuts("source,peer,is_up")
    def test_is_up(self, peer_result, is_up):
        assert peer_result["is_up"] == is_up


def transform_result(general_result) -> Dict[str, NutsResult]:
    return {source: nuts_result_wrapper(result, _transform_single_result) for source, result in general_result.items()}


def _transform_single_result(single_result: MultiResult) -> dict:
    task_result = single_result[0].result
    neighbors = task_result["bgp_neighbors"]
    if "global" not in neighbors:
        return {}
    global_scope = neighbors["global"]
    router_id = global_scope["router_id"]
    return {peer: _add_local_id(details, router_id) for peer, details in global_scope["peers"].items()}


def _add_local_id(element: dict, router_id: str) -> dict:
    element["local_id"] = router_id
    return element
