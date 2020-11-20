import pytest
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get

from pytest_nuts.helpers.converters import InterfaceNameConverter


@pytest.fixture(scope="class")
def nuts_task():
    return napalm_get


@pytest.fixture(scope="class")
def nuts_arguments():
    return {"getters": ["network_instances"]}


@pytest.fixture(scope="class")
def nornir_filter(hosts):
    return F(name__any=hosts)


@pytest.fixture(scope="class")
def hosts(nuts_parameters):
    return {entry["source"] for entry in nuts_parameters["test_data"]}


@pytest.fixture(scope="class")
def transformed_result(general_result):
    return transform_result(general_result)


class TestNapalmNetworkInstances:
    @pytest.mark.nuts("source,network_instance,interfaces")
    def test_network_instance_contains_interfaces(self, transformed_result, source, network_instance, interfaces):
        assert transformed_result[source][network_instance]["interfaces"] == interfaces

    @pytest.mark.nuts("source,network_instance,route_distinguisher")
    def test_route_distinguisher(self, transformed_result, source, network_instance, route_distinguisher):
        assert transformed_result[source][network_instance]["route_distinguisher"] == route_distinguisher


def transform_result(general_result):
    return {source: _transform_single_result(result) for source, result in general_result.items()}


def _transform_single_result(single_result):
    task_result = single_result[0].result
    network_instances = task_result["network_instances"]
    return {instance: _transform_single_network_instance(details) for instance, details in network_instances.items()}


def _transform_single_network_instance(network_instance):
    return {
        "route_distinguisher": _extract_route_distinguisher(network_instance),
        "interfaces": _extract_interfaces(network_instance),
    }


def _extract_route_distinguisher(element):
    return element["state"]["route_distinguisher"]


def _extract_interfaces(element):
    return list(element["interfaces"]["interface"].keys())
