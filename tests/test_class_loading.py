import pytest

from nuts import index
from tests.utils import YAML_EXTENSION

test_index = {"TestFixture": "tests.base_tests.class_loading"}


@pytest.fixture
def mock_index(monkeypatch):
    """Mocks index to a module"""
    monkeypatch.setattr(index, "default_index", test_index)


def test_load_class_and_execute_tests(pytester):
    arguments = {
        "test_class_loading": """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestClass
              test_data: []
            """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_load_class_multiple_times(pytester):
    arguments = {
        "test_load_class_repeatedly": """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestClass
              test_data: []
            - test_module: tests.base_tests.class_loading
              test_class: TestClass
              test_data: []
            """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=4)


def test_injects_arguments_as_fixture(pytester):
    arguments = {
        "test_args_as_fixture": """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestFixture
              test_data: ['test1', 'test2']
            """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_load_class_from_index(pytester, mock_index):
    arguments = {
        "test_index_loading": """
            ---
            - test_class: TestFixture
              test_data: ['test1', 'test2']
            """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_class_with_empty_test_execution_field(pytester):
    arguments = {
        "test_empty_execution_field": """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestTestExecutionParamsEmpty
              test_execution:
              test_data: ['test3', 'test4']
            """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_class_with_test_execution_field(pytester):
    arguments = {
        "test_execution_field": """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestTestExecutionParamsExist
              test_execution:
                count: 42
                ref: 23
              test_data: ['test3', 'test4']
            """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_bundle_with_labels(pytester):
    arguments = {
        "test_label_loading": """
        ---
        - test_module: tests.base_tests.class_loading
          label: testrun23
          test_class: TestClass
          test_data: ["alice"]
        - test_module: tests.base_tests.class_loading
          label: testrun42
          test_class: TestClass
          test_data: ["eliza"]
        """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest("--collect-only")
    result.stdout.fnmatch_lines(
        [
            "*NutsTestClass TestClass - testrun23*",
            "*NutsTestClass TestClass - testrun42*",
        ]
    )


def test_find_test_module_of_class(mock_index):
    path = index.find_test_module_of_class("TestFixture")
    expected = "tests.base_tests.class_loading"
    assert path == expected
