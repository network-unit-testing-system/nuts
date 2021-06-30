"""Fixtures"""
from typing import Optional, Dict, Any

import pytest
from _pytest.main import Session
from _pytest.nodes import Collector
from _pytest.python import Metafunc
from _pytest.fixtures import FixtureRequest
from _pytest.config import Config
from py._path.local import LocalPath

from nuts.context import NutsContext
from nuts.helpers.result import NutsResult
from nuts.yamlloader import NutsYamlFile, get_parametrize_data


@pytest.fixture(scope="class")
def nuts_ctx(request: FixtureRequest) -> NutsContext:
    params = request.node.params
    context_class = getattr(request.module, "CONTEXT", NutsContext)
    ctx = context_class(params)
    ctx.initialize()
    return ctx


@pytest.fixture
def single_result(nuts_ctx: NutsContext, nuts_test_entry: Dict[str, Any]) -> NutsResult:
    """
    Returns the result which belongs to a specific host
    out of the overall set of results that has been returned by nornir's task.
    In addition, ensures that the result has no exception and has not failed.

    :param nuts_ctx: The context for a test
    :param nuts_test_entry: The entry from the test bundle (yaml-file) for which
        the corresponding result should be returned
    :return: The `NutsResult` that belongs to a host or host/destination pair
    """
    res = nuts_ctx.extractor.single_result(nuts_test_entry)
    res.validate()
    return res


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "nuts: marks the test for nuts parametrization")


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """
    Checks if the the nuts pytest parametrization scheme exists (@pytest.mark.nuts)
    to generate tests based on that information.
    """
    nuts = metafunc.definition.get_closest_marker("nuts")
    if nuts:
        parametrize_args, parametrize_data = get_parametrize_data(
            metafunc, *nuts.args, **nuts.kwargs
        )
        metafunc.parametrize(parametrize_args, parametrize_data)


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent: Session, path: LocalPath) -> Optional[Collector]:
    """
    Performs the collection phase for the given pytest session.
    Collects all test bundles if available, i.e. files starting
    with 'test' and ending in .yaml.
    :param parent: pytest session object
    :param path: path to test file(s)
    :return: The pytest collector if found
    """
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)
    return None
