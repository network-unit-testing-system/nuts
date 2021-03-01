from tests.helpers.shared import YAML_EXTENSION


def test_load_module_fixture(testdir):
    arguments = {
        "test_module_level_fixtures": """
            ---
            - test_module: tests.base_tests.module_level_fixtures
              test_class: TestModuleLevelFixture
              test_data: []
            """
    }
    testdir.makefile(YAML_EXTENSION, **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_load_module_fixture_multiple_test_definitions(testdir):
    arguments = {
        "test_module_level_fixtures": """
            ---
            - test_module: tests.base_tests.module_level_fixtures
              test_class: TestModuleLevelFixture
              test_data: []
            """,
        "test_module_level_fixtures2": """
            ---
            - test_module: tests.base_tests.module_level_fixtures
              test_class: TestModuleLevelFixture
              test_data: []
            """,
    }
    testdir.makefile(YAML_EXTENSION, **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=2)


def test_load_module_fixture_with_test_execution_params(testdir):
    arguments = {
        "test_module_level_fixtures": """
            ---
            - test_module: tests.base_tests.module_level_fixtures
              test_class: TestModuleLevelFixture
              test_execution:
                count: 1
                call: 42
              test_data: []
            """
    }
    testdir.makefile(YAML_EXTENSION, **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
