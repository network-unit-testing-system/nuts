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
def nr(nornir_config_file):
    return InitNornir(config_file=nornir_config_file,
                      logging=False)


@pytest.fixture(scope="class")
def general_result(nr, nuts_task, nuts_arguments, nornir_filter):
    if nornir_filter:
        selected_hosts = nr.filter(nornir_filter)
    else:
        selected_hosts = nr
    overall_results = selected_hosts.run(task=nuts_task, **nuts_arguments)
    return overall_results


def pytest_generate_tests(metafunc):
    nuts = [mark.args for mark in metafunc.definition.own_markers if mark.name == 'nuts']
    # checks for @pytest.mark.nuts("input,expected", "placeholder")
    # nuts = [("input,expected", "placeholder")]
    if nuts and len(nuts) == 1:
        nuts_params = nuts[0]  # nuts_params = ("input,expected", "placeholder")
        assert nuts_params[1] == 'placeholder'
        fields = nuts_params[0].split(",")
        # actual_data = fetch_data_from_yaml_definition()
        actual_data = dict_to_tuple_list(metafunc.cls.nuts_parameters_x()['arguments'], fields)
        metafunc.parametrize(nuts_params[0], actual_data)


# https://docs.pytest.org/en/latest/example/nonpython.html#yaml-plugin
def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return NutsYamlFile.from_parent(parent, fspath=path)


def dict_to_tuple_list(source, fields):
    return [dict_to_tuple(item, fields) for item in source]


def dict_to_tuple(source, fields):
    ordered_fields = [source[field] for field in fields]
    return tuple(ordered_fields)



