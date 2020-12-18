import pytest

from pytest_nuts.index import ModuleIndex


@pytest.fixture
def custom_index():
    return {"testClass": "test.module"}


@pytest.fixture
def default_module_index(custom_index):
    return ModuleIndex(custom_index)


class TestConstructor:
    def test_initialises_index_if_no_index_is_specified(self):
        module_index = ModuleIndex()
        assert module_index.index is not None

    def test_saves_index_if_index_is_specified(self, custom_index):
        module_index = ModuleIndex(custom_index)
        assert module_index.index == custom_index


@pytest.mark.parametrize(
    "test_class, expected",
    [
        ("someClass", None),
        ("testClass", "test.module"),
    ],
)
def test_find_test_module_of_class(test_class, expected, default_module_index):
    assert default_module_index.find_test_module_of_class(test_class) == expected
