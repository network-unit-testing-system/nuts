from typing import Iterable, Union

import pytest
from _pytest.main import Session
from _pytest.python import Metafunc
from _pytest.fixtures import FixtureRequest
from _pytest import nodes
from _pytest.config import Config
from nornir import InitNornir
from nornir.core import Nornir
from py._path.local import LocalPath

from pytest_nuts.context import NutsContext, NornirNutsContext
from pytest_nuts.helpers.result import NutsResult
from pytest_nuts.yaml_to_test import NutsYamlFile, get_parametrize_data


@pytest.fixture
def nornir_config_file() -> str:
    return "nr-config.yaml"

    
@pytest.fixture(scope="session")
def initialized_nornir(nornir_config_file) -> Nornir:
    return InitNornir(config_file=nornir_config_file, logging=False)


@pytest.fixture
def nuts_ctx(request: FixtureRequest) -> NutsContext:
    ctx = request.node.parent.parent.nuts_ctx
    return ctx


@pytest.fixture
def nornir_nuts_ctx(nuts_ctx, initialized_nornir) -> NornirNutsContext:
    nuts_ctx.nornir = initialized_nornir
    return nuts_ctx


@pytest.fixture
def single_result(nornir_nuts_ctx, host: str) -> NutsResult:
    assert host in nornir_nuts_ctx.transformed_result, f"Host {host} not found in aggregated result."
    return nornir_nuts_ctx.transformed_result[host]


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
def pytest_collect_file(parent: Session, path: LocalPath) -> Iterable[Union[nodes.Item, nodes.Collector]]:
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)
    else:
        raise FileNotFoundError("No test file starting with 'test' and ending in .yaml found")
