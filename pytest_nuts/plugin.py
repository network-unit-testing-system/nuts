import pytest

from pytest_nuts.helpers.result import NutsResult
from pytest_nuts.yaml2test import NutsYamlFile


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


def get_parametrize_data(metafunc, nuts_params):
    fields = [field.strip() for field in nuts_params[0].split(",")]
    required_fields = calculate_required_fields(fields, nuts_params)
    nuts_test_instance = metafunc.definition.parent.parent
    data = getattr(nuts_test_instance, "params")
    if not data:
        return []
    return dict_to_tuple_list(data["test_data"], fields, required_fields)


def calculate_required_fields(fields, nuts_params):
    required_fields = set(fields)
    if len(nuts_params) >= 2:
        optional_fields = {field.strip() for field in nuts_params[1].split(",")}
        required_fields -= optional_fields
    return required_fields


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)


def dict_to_tuple_list(source, fields, required_fields):
    return [wrap_if_needed(item, required_fields, dict_to_tuple(item, fields)) for item in source]


def wrap_if_needed(source, required_fields, present_fields):
    missing_fields = required_fields - set(source)
    if not missing_fields:
        return present_fields
    return pytest.param(
        *present_fields, marks=pytest.mark.skip(f"required values {missing_fields} not present in test-bundle")
    )


def dict_to_tuple(source, fields):
    ordered_fields = [source.get(field) for field in fields]
    return tuple(ordered_fields)
