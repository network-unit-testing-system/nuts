from tests.helpers.selftest_helpers import YAML_EXTENSION


def test_skips_execution_without_arguments(testdir):
    arguments = {
        "test_class_loading": """
---
- test_module: tests.base_tests.simple_nuts_annotation
  test_class: TestKeyValue
            """
    }
    testdir.makefile(YAML_EXTENSION, **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(skipped=1)


class TestExecuteTests:
    def test_based_on_arguments(self, testdir):
        arguments = {
            "test_class_loading": """
    ---
    - test_module: tests.base_tests.simple_nuts_annotation
      test_class: TestKeyValue
      test_data: [{"key": "abc", "value":"abc"}, 
      {"key": "cde", "value":"cde"}]
                """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=2)

    def test_multiple_times_separates_arguments(self, testdir):
        arguments = {
            "test_class_loading": """
    ---
    - test_module: tests.base_tests.simple_nuts_annotation
      test_class: TestKeyValue
      test_data: [{"key": "abc", "value":"abc"}]
    - test_module: tests.base_tests.simple_nuts_annotation
      test_class: TestKeyValue
      test_data: [{"key": "abc", "value":"bcd"}]
                """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1, failed=1)


class TestOptionalAttributes:
    def test_skips_test_if_attribute_is_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestKeyValue
          test_data: [{"key": "abc"}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(skipped=1)

    def test_skips_test_if_non_optional_attribute_is_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestOptionalAttribute
          test_data: [{"key": "abc"}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(skipped=1)

    def test_executes_test_if_optional_attribute_is_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestOptionalAttribute
          test_data: [{"value": null}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

    def test_executes_test_if_any_optional_attribute_is_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestOptionalAttributes
          test_data: [{"value": null}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

    def test_executes_test_if_all_optional_attribute_are_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestOptionalAttributes
          test_data: [{}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

    def test_executes_test_if_required_attribute_is_none(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestKeyValue
          test_data: [{"key": null, "value": null}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

    def test_strips_spaced_attribute_names(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestSpacedKeyValue
          test_data: [{"key": null, "value": null}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

    def test_single_arguments(self, testdir):
        arguments = {
            "test_single_argument": """
            ---
            - test_module: tests.base_tests.simple_nuts_annotation
              test_class: TestSingleValue
              test_data: [{"value": "test"}]
                """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)
