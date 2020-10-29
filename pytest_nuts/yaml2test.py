import py
from pydoc import locate
from typing import Iterable, Union

import pytest
from _pytest import nodes, fixtures
from _pytest.python import Instance


class NutsYamlFile(pytest.File):

    def __init__(self, parent, fspath: py.path.local):
        super().__init__(fspath, parent)

    def collect(self):
        # We need a yaml parser, e.g. PyYAML.
        import yaml

        raw = yaml.safe_load(self.fspath.open())

        for test_entry in raw:
            module = load_test(test_entry["test_module"])
            yield NutsTestFile.from_parent(self, fspath=self.fspath, obj=module, test_entry=test_entry)

            # yield YamlItem.from_parent(self, test_class=test_entry["test_class"],  arguments=test_entry["arguments"])


def load_test(class_path):
    test_class = locate(class_path)
    return test_class


class NutsTestFile(pytest.Module):
    def __init__(self, fspath, parent, obj, test_entry):
        super().__init__(fspath, parent)
        self.obj = obj
        self.test_entry=test_entry
    
    def collect(self) -> Iterable[Union["Item", "Collector"]]:
        """
        Collects a single NutsTestClass instance from this NutsTestFile.
        At the start inject setup_module fixture and parse all fixtures from the module.
        This is directly adopted from pytest.Module
        """
        self._inject_setup_module_fixture()
        self._inject_setup_function_fixture()
        self.session._fixturemanager.parsefactories(self)

        class_name = self.test_entry["test_class"]
        label = self.test_entry.get("label")
        name = class_name if label is None else f'{class_name} - {label}'
        arguments = self.test_entry["arguments"]
        yield NutsTestClass.from_parent(self, name=name, class_name=class_name, arguments=arguments)


class NutsTestClass(pytest.Class):
    def __init__(self, parent, name: str, class_name: str, obj, **kw):
        super().__init__(name, parent=parent)
        self.params = kw
        self.name = name
        self.class_name = class_name

    def _getobj(self):
        """Get the underlying Python object.
        Overwritten from PyobjMixin to separate name and classname
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
        Similar to the injection of setup_class and setup_method in pytest.Class::collect
        """

        @fixtures.fixture(scope="class")
        def nuts_parameters(cls):
            return self.params

        def nuts_parameters_x():
            return self.params

        self.obj.nuts_parameters = nuts_parameters
        self.obj.nuts_parameters_x = nuts_parameters_x
        return super(NutsTestClass, self).collect()



