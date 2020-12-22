import pytest
from _pytest.python import Metafunc
from nornir import InitNornir

from pytest_nuts.helpers.result import NutsResult
from pytest_nuts.yaml2test import NutsYamlFile, get_parametrize_data


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


@pytest.fixture
def check_nuts_result(single_result: NutsResult) -> None:
    """
    Ensure that the result has no exception and is not failed.
    Raises corresponding AssertionError based on the condition

    :param single_result: The result to be checked
    :return: None
    :raise: AssertionError if single_result contains an exception or single_result is failed
    """
    assert not single_result.exception, "An exception was thrown during information gathering"
    assert not single_result.failed, "Information gathering failed"


def pytest_configure(config):
    config.addinivalue_line("markers", "nuts: marks the test for nuts parametrization")


def pytest_generate_tests(metafunc: Metafunc):
    """
    Checks if the the nuts pytest parametrization scheme exists (@pytest.mark.nuts)
    to generate tests based on that information. The placeholder later holds data retrieved
    from the YAML test definition.
    """
    nuts = metafunc.definition.get_closest_marker("nuts")
    if nuts:
        nuts_params = nuts.args
        parametrize_data = get_parametrize_data(metafunc, nuts_params)
        metafunc.parametrize(nuts_params[0], parametrize_data)


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)
