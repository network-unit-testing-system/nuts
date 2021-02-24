from typing import Iterable, Union, Optional

import pytest
from _pytest.main import Session
from _pytest.nodes import Collector
from _pytest.python import Metafunc
from _pytest.fixtures import FixtureRequest
from _pytest.config import Config
from nornir import InitNornir
from nornir.core import Nornir
from py._path.local import LocalPath
from pytest_nuts.helpers.errors import NutsUsageError, NutsSetupError

from pytest_nuts.context import NutsContext, NornirNutsContext
from pytest_nuts.helpers.result import NutsResult
from pytest_nuts.yaml_to_test import NutsYamlFile, get_parametrize_data


@pytest.fixture
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
    return InitNornir(config_file=nornir_config_file, logging=False)


@pytest.fixture
def nuts_ctx(request: FixtureRequest) -> NutsContext:
    ctx = request.node.parent.parent.nuts_ctx
    return ctx


@pytest.fixture
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
    The fixture that is passed on to the pytest test class. It returns the result that belongs to a
    specific host out of the overall set of results that has been returned by nornir's task.

    :param nornir_nuts_ctx: The context for a test with an initialized nornir instance
    :param host: The host for which the corresponding result should be returned
    :return: The `NutsResult` that belongs to a host
    """
    assert host in nornir_nuts_ctx.transformed_result, f"Host {host} not found in aggregated result."
    return nornir_nuts_ctx.transformed_result[host]


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
    to generate tests based on that information. The placeholder later holds data retrieved
    from the YAML test definition.
    """
    nuts = metafunc.definition.get_closest_marker("nuts")
    if nuts:
        nuts_params = nuts.args
        parametrize_data = get_parametrize_data(metafunc, nuts_params)
        metafunc.parametrize(nuts_params[0], parametrize_data)


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent: Session, path: LocalPath) -> Optional[Collector]:
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)
    return None
