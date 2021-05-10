"""Converts a test bundle (YAML file) into a test class for pytest.
Based on https://docs.pytest.org/en/stable/example/nonpython.html#yaml-plugin
"""
import importlib
import types
from importlib import util
from typing import Iterable, Union, Any, Optional, List, Set, Dict, Tuple

import pytest
import yaml
from _pytest import nodes
from _pytest.mark import ParameterSet
from _pytest.nodes import Node
from _pytest.python import Metafunc

from nuts.helpers.errors import NutsUsageError
from nuts.index import ModuleIndex


class NutsYamlFile(pytest.File):
    def collect(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        with self.fspath.open() as f:
            raw = yaml.safe_load(f)

        for test_entry in raw:
            module_path = find_module_path(test_entry.get("test_module"), test_entry.get("test_class"))
            module = load_module(module_path)
            yield NutsTestFile.from_parent(self, fspath=self.fspath, obj=module, test_entry=test_entry)


def find_module_path(module_path: Optional[str], class_name: str) -> str:
    if not class_name:
        raise NutsUsageError("Class name of the specific test missing in YAML file.")
    if not module_path:
        module_path = ModuleIndex().find_test_module_of_class(class_name)
        if not module_path:
            raise NutsUsageError(f"A module that corresponds to the test_class called {class_name} could not be found.")
    return module_path


def load_module(module_path: str) -> types.ModuleType:
    spec = util.find_spec(module_path)
    if spec is None:
        raise NutsUsageError(f"Module path called {module_path} not found.")
    module = util.module_from_spec(spec)
    # https://github.com/python/typeshed/issues/2793
    assert isinstance(spec.loader, importlib.abc.Loader)
    spec.loader.exec_module(module)
    return module


class NutsTestFile(pytest.Module):
    def __init__(self, obj: Any, test_entry: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.obj = obj
        self.test_entry = test_entry

    def collect(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        """
        Collects a single NutsTestClass instance from this NutsTestFile.
        At the start inject setup_module fixture and parse all fixtures from the module.
        This is directly adopted from pytest.Module.
        """

        self._inject_setup_module_fixture()
        self._inject_setup_function_fixture()
        self.session._fixturemanager.parsefactories(self)

        class_name = self.test_entry["test_class"]
        label = self.test_entry.get("label")
        name = class_name if label is None else f"{class_name} - {label}"

        test_data = self.test_entry.get("test_data", [])
        test_execution = self.test_entry.get("test_execution")
        yield NutsTestClass.from_parent(
            self, name=name, class_name=class_name, test_data=test_data, test_execution=test_execution
        )


class NutsTestClass(pytest.Class):
    """
    Custom nuts test collector for test methods.
    Initialises a corresponding context with externally provided parameters.
    """

    def __init__(self, parent: NutsTestFile, name: str, class_name: str, **kw):
        super().__init__(name, parent=parent)
        self.params = kw
        self.name = name
        self.class_name = class_name

    def _getobj(self) -> Any:
        """
        Get the underlying Python object.
        Overwritten from PyobjMixin to separate name and classname.
        This allows to group multiple tests of the same class with different parameters to be grouped separately.
        """
        # cf. https://github.com/pytest-dev/pytest/blob/master/src/_pytest/python.py
        assert self.parent is not None
        obj = self.parent.obj  # type: ignore[attr-defined]
        return getattr(obj, self.class_name)

    @classmethod
    def from_parent(cls, parent: Node, *, name: str, obj=None, **kw) -> Any:  # type: ignore[override]
        """The public constructor."""
        # mypy throws an error because the parent class (pytest.Class) does not accept additional **kw
        # has been fixed in: https://github.com/pytest-dev/pytest/pull/8367
        # and will be part of a future pytest release. Until then, mypy is instructed to ignore this error
        return cls._create(parent=parent, name=name, obj=obj, **kw)


def get_parametrize_data(metafunc: Metafunc, nuts_params: Tuple[str, ...]) -> Union[list, List[ParameterSet]]:
    """
    Transforms externally provided parameters to be used in parametrized tests.
    :param metafunc: The annotated test function that will use the parametrized data.
    :param nuts_params: The fields used in a test and indicated via a custom pytest marker.
    :return: List of tuples that contain each the parameters for a test.
    """
    fields = [field.strip() for field in nuts_params[0].split(",")]
    required_fields = calculate_required_fields(fields, nuts_params)
    assert metafunc.definition.parent is not None
    nuts_test_instance = metafunc.definition.parent.parent
    data = getattr(nuts_test_instance, "params", None)
    if not data:
        return []
    return dict_to_tuple_list(data["test_data"], fields, required_fields)


def calculate_required_fields(fields: List[str], nuts_params: Tuple[str, ...]) -> Set[str]:
    required_fields = set(fields)
    if len(nuts_params) >= 2:
        optional_fields = {field.strip() for field in nuts_params[1].split(",")}
        required_fields -= optional_fields
    return required_fields


def dict_to_tuple_list(source: List[Dict], fields: List[str], required_fields: Set[str]) -> List[ParameterSet]:
    return [wrap_if_needed(item, required_fields, dict_to_tuple(item, fields)) for item in source]


def wrap_if_needed(source: Dict, required_fields: Set[str], present_fields: Tuple[Optional[Any], ...]) -> ParameterSet:
    missing_fields = required_fields - set(source)
    if not missing_fields:
        return pytest.param(*present_fields)
    return pytest.param(
        *present_fields, marks=pytest.mark.skip(f"required values {missing_fields} not present in test-bundle")
    )


def dict_to_tuple(source: Dict, fields: List[str]) -> Tuple[Optional[Any], ...]:
    ordered_fields = [source.get(field) for field in fields]
    return tuple(ordered_fields)
