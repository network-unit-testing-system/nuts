from tests.utils import YAML_EXTENSION


def test_load_module_fixture(pytester):
    arguments = {
        "test_module_level_fixtures": """
            ---
            - test_module: tests.base_tests.module_level_fixtures
              test_class: TestModuleLevelFixture
              test_data: []
            """
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_load_module_fixture_multiple_test_definitions(pytester):
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
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
