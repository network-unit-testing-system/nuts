from tests.helpers.selftest_helpers import YAML_EXTENSION


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
