from pydoc import locate
import py
from typing import Iterable, Union
import pytest

import yaml

from _pytest import nodes, fixtures
from _pytest.python import Instance

from nornir import InitNornir


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


def load_test(class_path):
    test_class = locate(class_path)
    return test_class



class NutsYamlFile(pytest.File):

    def __init__(self, parent, fspath: py.path.local):
        super().__init__(fspath, parent)

    def collect(self):
        # We need a yaml parser, e.g. PyYAML.
        import yaml

        raw = yaml.safe_load(self.fspath.open())

        for test_entry in raw:
            module = load_test(test_entry["test_module"])
            parent = NutsTestFile.from_parent(self, fspath=self.fspath, obj=module)
            class_name = test_entry["test_class"]
            label = test_entry.get("label")
            name = class_name if label is None else f'{class_name} - {label}'
            arguments = test_entry["arguments"]
            yield NutsTestClass.from_parent(parent, name=name, class_name=class_name, arguments=arguments)
            # yield YamlItem.from_parent(self, test_class=test_entry["test_class"],  arguments=test_entry["arguments"])


class NutsTestFile(pytest.File):
    def __init__(self, fspath, parent, obj):
        super().__init__(fspath, parent)
        self.obj = obj


class NutsTestClass(pytest.Class):
    def __init__(self, parent, name: str, class_name: str, obj, **kw):
        super().__init__(name, parent=parent)
        self.params = kw
        self.name = name
        self.class_name = class_name

    def _getobj(self):
        """Get the underlying Python object. Overwritten from PyobjMixin to separate name and classname
        This allows to group multiple tests of the same class with different parameters to be grouped separately"""
        # TODO: Improve the type of `parent` such that assert/ignore aren't needed.
        assert self.parent is not None
        obj = self.parent.obj  # type: ignore[attr-defined]
        return getattr(obj, self.class_name)

    @classmethod
    def from_parent(cls, parent, *, name, obj=None, **kw):
        """The public constructor."""
        return cls._create(parent=parent, name=name, obj=obj, **kw)

    def collect(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        """Inject custom nuts fixture into the test classes
        Similar to Class::collect
        Note that this prevents setup_class and setup_method fixtures to kick in"""

        @fixtures.fixture(scope="class")
        def nuts_parameters(cls):
            return self.params

        def nuts_parameters_x():
            return self.params

        self.obj.nuts_parameters = nuts_parameters
        self.obj.nuts_parameters_x = nuts_parameters_x
        return [(Instance.from_parent(self, name="()"))]



def dict_to_tuple_list(source, fields):
    return [dict_to_tuple(item, fields) for item in source]


def dict_to_tuple(source, fields):
    ordered_fields = [source[field] for field in fields]
    return tuple(ordered_fields)



