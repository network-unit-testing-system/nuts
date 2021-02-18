import types
from importlib import util
from typing import Iterable, Union, Any, Optional, List, Set, Dict, Tuple

import py
import pytest
import yaml
from _pytest import nodes

from pytest_nuts.context import NutsContext
from pytest_nuts.index import ModuleIndex


class NutsYamlFile(pytest.File):
    def __init__(self, parent, fspath: py.path.local):
        super().__init__(fspath, parent)

    def collect(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        with self.fspath.open() as f:
            raw = yaml.safe_load(f)

        for test_entry in raw:
            module = load_module(test_entry.get("test_module"), test_entry.get("test_class"))
            yield NutsTestFile.from_parent(self, fspath=self.fspath, obj=module, test_entry=test_entry)


def load_module(module_path: str, class_name: Optional[str]) -> types.ModuleType:
    if not module_path:
        module_path = ModuleIndex().find_test_module_of_class(class_name)
    spec = util.find_spec(module_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NutsTestFile(pytest.Module):
    def __init__(self, fspath, parent, obj, test_entry):
        super().__init__(fspath, parent)
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

    def __init__(self, parent: NutsTestFile, name: str, class_name: str, obj: Any, **kw):
        super().__init__(name, parent=parent)
        self.params = kw
        self.name = name
        self.class_name = class_name
        self.nuts_ctx = None

    def _getobj(self) -> Any:
        """
        Get the underlying Python object.
        Overwritten from PyobjMixin to separate name and classname.
        This allows to group multiple tests of the same class with different parameters to be grouped separately.
        """
        return getattr(self.parent.obj, self.class_name)

    @classmethod
    def from_parent(cls, parent: Node, *, name: str, obj=None, **kw: Any) -> Any:
        """The public constructor."""
        return cls._create(parent=parent, name=name, obj=obj, **kw)

    def collect(self) -> Iterable[Union[nodes.Item, nodes.Collector]]:
        """
        Collects all tests and instantiates the corresponding context.
        """
        if hasattr(self.module, "CONTEXT"):
            context = self.module.CONTEXT(self.params)
            self.nuts_ctx = context
        else:
            self.nuts_ctx = NutsContext(self.params)

        return super().collect()


def get_parametrize_data(metafunc: Metafunc, nuts_params: Tuple[str]) -> Union[list, List[ParameterSet]]:
    """
    Transforms externally provided parameters to be used in parametrized tests.
    :param metafunc: The annotated test function that will use the parametrized data.
    :param nuts_params: The fields used in a test and indicated via a custom pytest marker.
    :return: List of tuples that contain each the parameters for a test.
    """
    fields = [field.strip() for field in nuts_params[0].split(",")]
    required_fields = calculate_required_fields(fields, nuts_params)
    nuts_test_instance = metafunc.definition.parent.parent
    data = getattr(nuts_test_instance, "nuts_ctx", None)
    if not data:
        return []
    return dict_to_tuple_list(data.nuts_parameters["test_data"], fields, required_fields)


def calculate_required_fields(fields: List[str], nuts_params: Tuple[str]) -> Set[str]:
    required_fields = set(fields)
    if len(nuts_params) >= 2:
        optional_fields = {field.strip() for field in nuts_params[1].split(",")}
        required_fields -= optional_fields
    return required_fields


def dict_to_tuple_list(source: List[Dict], fields: List[str], required_fields: Set[str]) -> List[ParameterSet]:
    return [wrap_if_needed(item, required_fields, dict_to_tuple(item, fields)) for item in source]


def wrap_if_needed(source: Dict, required_fields: Set[str], present_fields: Tuple[str]) -> ParameterSet:
    missing_fields = required_fields - set(source)
    if not missing_fields:
        return pytest.param(*present_fields)
    return pytest.param(
        *present_fields, marks=pytest.mark.skip(f"required values {missing_fields} not present in test-bundle")
    )


def dict_to_tuple(source: Dict, fields: List[str]) -> Tuple[Optional[Any]]:
    ordered_fields = [source.get(field) for field in fields]
    return tuple(ordered_fields)
