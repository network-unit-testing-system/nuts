import pytest

from pytest_nuts.index import ModuleIndex


class TestConstructor:
    def test_initialises_index_if_no_index_is_specified(self):
        module_index = ModuleIndex()
        assert module_index.index is not None

    def test_saves_index_if_index_is_specified(self):
        custom_index = {"testClass": "test.module"}
        module_index = ModuleIndex(custom_index)
        assert module_index.index == custom_index


@pytest.fixture
def default_module_index():
    return ModuleIndex({"testClass": "test.module"})


class TestFindTestModuleOfClass:
    def test_returns_none_if_class_not_specified(self, default_module_index):
        assert default_module_index.find_test_module_of_class("someClass") is None

    def test_returns_module_if_class_is_specified(self, default_module_index):
        assert default_module_index.find_test_module_of_class("testClass") == "test.module"
