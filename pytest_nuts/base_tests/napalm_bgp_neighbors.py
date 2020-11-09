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

    @pytest.mark.nuts("source,local_id,local_as,peer,remote_as,remote_id,is_enabled,is_up", "placeholder")
    def test_neighbor_full(
        self, transformed_result, source, local_id, local_as, peer, remote_as, remote_id, is_enabled, is_up
    ):
        bgp_neighbor_entry = transformed_result[source][peer]
        assert bgp_neighbor_entry["local_id"] == local_id
        assert bgp_neighbor_entry["local_as"] == local_as
        assert bgp_neighbor_entry["remote_as"] == remote_as
        assert bgp_neighbor_entry["remote_id"] == remote_id
        assert bgp_neighbor_entry["is_enabled"] == is_enabled
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
