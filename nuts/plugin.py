"""Fixtures"""
from typing import Optional

import pytest
from _pytest.main import Session
from _pytest.nodes import Collector
from _pytest.python import Metafunc
from _pytest.fixtures import FixtureRequest
from _pytest.config import Config
from nornir import InitNornir
from nornir.core import Nornir
from py._path.local import LocalPath
from nuts.helpers.errors import NutsSetupError

from nuts.context import NutsContext, NornirNutsContext
from nuts.helpers.result import NutsResult
from nuts.yamlloader import NutsYamlFile, get_parametrize_data


@pytest.fixture(scope="session")
def nornir_config_file() -> str:
    """
    Returns the filename to a nornir configuration file.
    https://nornir.readthedocs.io/en/stable/configuration/index.html

    :return: The filename of the configuration
    """
    return "nr-config.yaml"


@pytest.fixture(scope="session")
def initialized_nornir(nornir_config_file: str) -> Nornir:
    """
    Initalizes nornir with a provided configuration file.

    :param nornir_config_file: The filename of a nornir configuration file
    :return: An initialized nornir instance
    """
    return InitNornir(config_file=nornir_config_file, logging={"enabled": False})


@pytest.fixture(scope="class")
def nuts_ctx(request: FixtureRequest) -> NutsContext:
    params = request.node.params
    context_class = getattr(request.module, "CONTEXT", NutsContext)
    return context_class(params)


@pytest.fixture(scope="class")
def nornir_nuts_ctx(nuts_ctx: NutsContext, initialized_nornir: Nornir) -> NornirNutsContext:
    """
    Injects an initialized nornir instance in the context of a test.

    :param nuts_ctx: The context to which the nornir instance should be added
    :param initialized_nornir: The nornir instance
    :return: A NornirNutsContext with an initialized nornir instance
    """
    if not isinstance(nuts_ctx, NornirNutsContext):
        raise NutsSetupError("The initialized context does not support the injection of nornir.")
    nuts_ctx.nornir = initialized_nornir
    return nuts_ctx


@pytest.fixture
def single_result(nornir_nuts_ctx: NornirNutsContext, host: str) -> NutsResult:
    """
    Returns the result which belongs to a specific host out of the overall set of results
    that has been returned by nornir's task.

    :param nornir_nuts_ctx: The context for a test with an initialized nornir instance
    :param host: The host for which the corresponding result should be returned
    :return: The `NutsResult` that belongs to a host
    """
    result = nornir_nuts_ctx.transformed_result()
    assert host in result, f"Host {host} not found in aggregated result."
    return result[host]


@pytest.fixture
def check_nuts_result(single_result: NutsResult) -> None:
    """
    Ensure that the result has no exception and has not failed.
    Raises corresponding AssertionError based on the condition.

    :param single_result: The result to be checked
    :return: None
    :raise: AssertionError if single_result contains an exception or single_result is failed
    """
    assert not single_result.exception, "An exception was thrown during information gathering"
    assert not single_result.failed, "Information gathering failed"


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "nuts: marks the test for nuts parametrization")


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """
    Checks if the the nuts pytest parametrization scheme exists (@pytest.mark.nuts)
    to generate tests based on that information.
    """
    nuts = metafunc.definition.get_closest_marker("nuts")
    if nuts:
        parametrize_data = get_parametrize_data(metafunc, nuts.args)
        metafunc.parametrize(nuts.args[0], parametrize_data)


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent: Session, path: LocalPath) -> Optional[Collector]:
    """
    Performs the collection phase for the given pytest session. Collects all test bundles if available,
    i.e. files starting with 'test' and ending in .yaml.
    :param parent: pytest session object
    :param path: path to test file(s)
    :return: The pytest collector if found
    """
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)
    return None
