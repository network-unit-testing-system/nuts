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

from nuts.helpers.errors import NutsUsageError, NutsSetupError
from nuts import index


class NutsYamlFile(pytest.File):
    """
    Collect tests from a yaml file.
    """

    def collect(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        # path uses pathlib.Path and is meant to
        #   replace fspath, which uses py.path.local
        # both variants will be used for some time in parallel within pytest.
        # If fspath is used in a newer pytest version,
        #   it triggers a deprecation warning.
        # We therefore use a wrapper that can use both path types
        if hasattr(self, "path"):
            yield from self._collect_path()
        else:
            yield from self._collect_fspath()

    def _collect_path(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        try:
            with self.path.open() as fo:  # type: ignore[attr-defined]
                raw = yaml.safe_load(fo)
        except OSError as ex:
            raise NutsSetupError(
                f"Could not open YAML file containing test bundle:\n{ex}"
            )

        for test_entry in raw:
            module = find_and_load_module(test_entry)
            yield NutsTestFile.from_parent(  # type: ignore[call-arg]
                self,
                path=self.path,  # type: ignore[attr-defined, call-arg]
                obj=module,
                test_entry=test_entry,
            )

    def _collect_fspath(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        try:
            with self.fspath.open() as f:
                raw = yaml.safe_load(f)
        except OSError as e:
            raise NutsSetupError(
                f"Could not open YAML file containing test bundle:\n{e}"
            )

        for test_entry in raw:
            module = find_and_load_module(test_entry)
            yield NutsTestFile.from_parent(
                self, fspath=self.fspath, obj=module, test_entry=test_entry
            )


def find_and_load_module(test_entry: Dict[str, str]) -> types.ModuleType:
    test_class = test_entry.get("test_class")
    if not test_class:
        raise NutsUsageError("Class name of the specific test missing in YAML file.")
    module_path = find_module_path(test_entry.get("test_module"), test_class)
    return load_module(module_path)


def find_module_path(module_path: Optional[str], class_name: str) -> str:
    if not module_path:
        module_path = index.find_test_module_of_class(class_name)
        if not module_path:
            raise NutsUsageError(
                f"A module that corresponds to the test_class "
                f"called {class_name} could not be found."
            )
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
    """
    Custom nuts collector for test classes and functions.
    """

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
            self,
            name=name,
            class_name=class_name,
            test_data=test_data,
            test_execution=test_execution,
        )


class NutsTestClass(pytest.Class):
    """
    Custom nuts test collector for test methods.
    Initialises a corresponding context with externally provided parameters.
    """

    def __init__(self, parent: NutsTestFile, name: str, class_name: str, **kw: Any):
        super().__init__(name, parent=parent)
        self.params: Any = kw
        self.name: str = name
        self.class_name: str = class_name

    def _getobj(self) -> Any:
        """
        Get the underlying Python object.
        Overwritten from PyobjMixin to separate name and classname.
        This allows to group multiple tests of the same class with
        different parameters to be grouped separately.
        """
        # cf. https://github.com/pytest-dev/pytest/blob/master/src/_pytest/python.py
        assert self.parent is not None
        obj = self.parent.obj  # type: ignore[attr-defined]
        return getattr(obj, self.class_name)

    @classmethod
    def from_parent(  # type: ignore[override]
        cls, parent: Node, *, name: str, obj: Any = None, **kw: Any
    ) -> Any:
        """The public constructor."""
        # mypy throws an error because the parent
        #   class (pytest.Class) does not accept additional **kw
        # has been fixed in: https://github.com/pytest-dev/pytest/pull/8367
        # and will be part of a future pytest release. Until then,
        #   mypy is instructed to ignore this error
        return cls._create(parent=parent, name=name, obj=obj, **kw)


def get_parametrize_data(
    metafunc: Metafunc, nuts_params: Tuple[str, ...]
) -> List[ParameterSet]:
    """
    Transforms externally provided parameters to be used in parametrized tests.
    :param metafunc: The annotated test function that will use the parametrized data.
    :param nuts_params: The fields used in a test and indicated
        via a custom pytest marker.
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


def calculate_required_fields(
    fields: List[str], nuts_params: Tuple[str, ...]
) -> Set[str]:
    required_fields = set(fields)
    if len(nuts_params) >= 2:
        optional_fields = {field.strip() for field in nuts_params[1].split(",")}
        required_fields -= optional_fields
    return required_fields


def dict_to_tuple_list(
    test_data: List[Dict[str, Any]], fields: List[str], required_fields: Set[str]
) -> List[ParameterSet]:
    return [
        wrap_if_needed(item, required_fields, dict_to_tuple(item, fields))
        for item in test_data
    ]


def wrap_if_needed(
    source: Dict[str, Any],
    required_fields: Set[str],
    present_fields: Tuple[Optional[Any], ...],
) -> ParameterSet:
    missing_fields = required_fields - set(source)
    if not missing_fields:
        return pytest.param(*present_fields)
    return pytest.param(
        *present_fields,
        marks=pytest.mark.skip(
            f"required values {missing_fields} not present in test-bundle"
        ),
    )


def dict_to_tuple(
    source: Dict[str, Any], fields: List[str]
) -> Tuple[Optional[Any], ...]:
    ordered_fields = [source.get(field) for field in fields]
    return tuple(ordered_fields)