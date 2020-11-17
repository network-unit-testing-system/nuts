import pytest
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get


class TestNapalmBgpNeighbors:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return napalm_get

    @pytest.fixture(scope="class")
    def nuts_arguments(self):
        return {"getters": ["bgp_neighbors"]}

    @pytest.fixture(scope="class")
    def nornir_filter(self, hosts):
        return F(name__any=hosts)

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["source"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        return transform_result(general_result)

    @pytest.mark.nuts("source,peer,local_as")
    def test_local_as(self, transformed_result, source, peer, local_as):
        bgp_neighbor_entry = transformed_result[source][peer]
        assert bgp_neighbor_entry["local_as"] == local_as

    @pytest.mark.nuts("source,peer,local_id")
    def test_local_id(self, transformed_result, source, peer, local_id):
        bgp_neighbor_entry = transformed_result[source][peer]
        assert bgp_neighbor_entry["local_id"] == local_id

    @pytest.mark.nuts("source,peer,remote_as")
    def test_remote_as(self, transformed_result, source, peer, remote_as):
        bgp_neighbor_entry = transformed_result[source][peer]
        assert bgp_neighbor_entry["remote_as"] == remote_as

    @pytest.mark.nuts("source,peer,remote_id")
    def test_remote_id(self, transformed_result, source, peer, remote_id):
        bgp_neighbor_entry = transformed_result[source][peer]
        assert bgp_neighbor_entry["remote_id"] == remote_id

    @pytest.mark.nuts("source,peer,is_enabled")
    def test_is_enabled(self, transformed_result, source, peer, is_enabled):
        bgp_neighbor_entry = transformed_result[source][peer]
        assert bgp_neighbor_entry["is_enabled"] == is_enabled

    @pytest.mark.nuts("source,peer,is_up")
    def test_is_up(self, transformed_result, source, peer, is_up):
        bgp_neighbor_entry = transformed_result[source][peer]
        assert bgp_neighbor_entry["is_up"] == is_up


def transform_result(general_result):
    return {source: _transform_single_result(result) for source, result in general_result.items()}


def _transform_single_result(single_result):
    task_result = single_result[0].result
    neighbors = task_result["bgp_neighbors"]
    if "global" not in neighbors:
        return {}
    global_scope = neighbors["global"]
    router_id = global_scope["router_id"]
    return {peer: _add_local_id(details, router_id) for peer, details in global_scope["peers"].items()}


def _add_local_id(element, router_id):
    element["local_id"] = router_id
    return element
