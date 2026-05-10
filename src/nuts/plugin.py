"""Fixtures"""

from typing import Optional, Dict, Any
from pathlib import Path

import pytest
from pytest import Parser
from pytest import Session
from pytest import Collector
from pytest import Metafunc
from pytest import FixtureRequest
from pytest import Config

from nuts.context import NutsContext
from nuts.context import NornirNutsContext
from nuts.helpers.result import NutsResult
from nuts.yamlloader import NutsYamlFile, get_parametrize_data


def pytest_addhooks(pluginmanager):
    from nuts import hooks

    pluginmanager.add_hookspecs(hooks)


@pytest.fixture(scope="class")
def nuts_ctx(request: FixtureRequest) -> NutsContext:
    params = request.node.params
    context_class = getattr(request.module, "CONTEXT", NutsContext)
    ctx: NutsContext = context_class(params, pytestconfig=request.config)
    ctx.initialize()
    return ctx


@pytest.fixture
def single_result(
    nuts_ctx: NutsContext, nuts_test_entry: Dict[str, Any], request: FixtureRequest
) -> NutsResult:
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

    # Invoke the pytest_nuts_single_result hook to extend result reports.
    request.config.hook.pytest_nuts_single_result(
        request=request, nuts_ctx=nuts_ctx, result=res
    )

    return res


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "nuts: marks the test for nuts parametrization")


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """
    Checks if the nuts pytest parametrization scheme exists (@pytest.mark.nuts)
    to generate tests based on that information.
    """
    nuts = metafunc.definition.get_closest_marker("nuts")
    if nuts:
        parametrize_args, parametrize_data = get_parametrize_data(
            metafunc, *nuts.args, **nuts.kwargs
        )
        metafunc.parametrize(parametrize_args, parametrize_data)


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent: Session, file_path: Path) -> Optional[Collector]:
    """
    Performs the collection phase for the given pytest session.
    Collects all test bundles if available, i.e. files starting
    with 'test' and ending in .yaml or .yml.
    :param parent: pytest session object
    :param file_path: path to test file(s)
    :return: The pytest collector if found
    """
    if file_path.suffix in [".yaml", ".yml"] and file_path.name.startswith("test"):
        return NutsYamlFile.from_parent(parent, path=file_path)
    return None


def pytest_addoption(parser: Parser) -> None:
    """Add pytest command line options to configure nuts"""

    group = parser.getgroup("nuts")
    # Nornir context specific parameters
    group.addoption(
        "--nornir-config",
        "--nornir-configuration",
        action="store",
        dest="nornir_configuration",
        default=NornirNutsContext.DEFAULT_NORNIR_CONFIG_FILE,
        metavar="NORNIR_CONFIG",
        help="nuts nornir configuration file. Default is nr-config.yaml",
    )

    group.addoption(
        "--nornir-cache-disable",
        action="store_true",
        dest="nornir_cache_disabled",
        default=False,
        help="disable caching of nornir inventory between executions",
    )

    group.addoption(
        "--nornir-cached-inventory",
        action="store_true",
        dest="nornir_cached_inventory",
        default=False,
        help="Uses the chached inventory from the last executions if possible",
    )


def pytest_sessionstart(session: Session) -> None:
    """Called after the ``Session`` object has been created
    and before performing collection and entering the run test loop.

    :param pytest.Session session: The pytest session object.
    """
    if not session.config.getoption("nornir_cached_inventory") and session.config.cache:
        session.config.cache.set("nuts/NORNIR_CACHE", None)
