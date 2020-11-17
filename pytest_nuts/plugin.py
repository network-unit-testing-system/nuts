import pytest
from nornir import InitNornir

from pytest_nuts.yaml2test import NutsYamlFile


@pytest.fixture(scope="session")
def nornir_config_file():
    return "nr-config.yaml"


@pytest.fixture(scope="class")
def nuts_arguments():
    return {}


@pytest.fixture(scope="class")
def nornir_filter():
    return None


@pytest.fixture(scope="session")
def initialized_nornir(nornir_config_file):
    return InitNornir(config_file=nornir_config_file, logging=False)


@pytest.fixture(scope="class")
def general_result(initialized_nornir, nuts_task, nuts_arguments, nornir_filter):
    if nornir_filter:
        selected_hosts = initialized_nornir.filter(nornir_filter)
    else:
        selected_hosts = initialized_nornir
    overall_results = selected_hosts.run(task=nuts_task, **nuts_arguments)
    return overall_results


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "nuts: marks the test for nuts parameterization")


def pytest_generate_tests(metafunc):
    """
    Checks if the the nuts pytest parametrization scheme exists (@pytest.mark.nuts)
    to generate tests based on that information. The placeholder later holds data retrieved
    from the YAML test definition.
    """
    nuts = [mark.args for mark in metafunc.definition.own_markers if mark.name == "nuts"]
    if nuts and len(nuts) == 1:
        nuts_params = nuts[0]
        assert nuts_params[1] == "placeholder"

        parametrize_data = get_parametrize_data(metafunc, nuts_params)
        metafunc.parametrize(nuts_params[0], parametrize_data)


def get_parametrize_data(metafunc, nuts_params):
    fields = nuts_params[0].split(",")
    func = getattr(metafunc.cls, "get_parametrizing_data", None)
    if not func:
        return []
    return dict_to_tuple_list(metafunc.cls.get_parametrizing_data(), fields)


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)


def dict_to_tuple_list(source, fields):
    return [dict_to_tuple(item, fields) for item in source]


def dict_to_tuple(source, fields):
    ordered_fields = [source[field] for field in fields]
    return tuple(ordered_fields)
