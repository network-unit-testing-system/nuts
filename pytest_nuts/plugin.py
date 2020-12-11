import pytest

from pytest_nuts.helpers.result import NutsResult
from pytest_nuts.yaml2test import NutsYamlFile, get_parametrize_data


@pytest.fixture
def nuts_ctx(request):
    return request.node.parent.parent.nuts_ctx


@pytest.fixture
def single_result(nuts_ctx, host):
    assert host in nuts_ctx.transformed_result, f"Host {host} not found in aggregated result."
    return nuts_ctx.transformed_result[host]


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


def pytest_generate_tests(metafunc):
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
