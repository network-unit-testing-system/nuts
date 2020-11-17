from tests.helpers.shared import YAML_EXTENSION


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

    def test_inserts_none_on_incomplete_data(self, testdir):
        arguments = {
            "test_class_loading": """
    ---
    - test_module: tests.base_tests.simple_nuts_annotation
      test_class: TestNonPresentValue
      test_data: [{"key": "abc"}]
                """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

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

    def test_errors_without_placeholder(self, testdir):
        arguments = {
            "test_class_loading": """
    ---
    - test_module: tests.base_tests.simple_nuts_annotation
      test_class: TestKeyValueWithoutPlaceholder
      test_data: [{"key": "abc", "value":"abc"}]
                """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(errors=1)


class TestRequiredAttributes:
    def test_skips_test_if_required_attribute_is_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestRequiredAttribute
          test_data: [{"key": "abc"}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(skipped=1)

    def test_skips_test_if_any_required_attribute_is_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestRequiredAttributes
          test_data: [{"key": "abc"}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(skipped=1)

    def test_skips_tests_if_multiple_required_attributes_are_missing(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestRequiredAttributes
          test_data: [{}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(skipped=1)

    def test_executes_test_if_required_attribute_is_present(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestRequiredAttribute
          test_data: [{"key":"value", "value": "value"}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

    def test_executes_test_if_required_attribute_is_None(self, testdir):
        arguments = {
            "test_class_loading": """
        ---
        - test_module: tests.base_tests.simple_nuts_annotation
          test_class: TestRequiredAttributes
          test_data: [{"key": null, "value": null}]
                    """
        }
        testdir.makefile(YAML_EXTENSION, **arguments)

        result = testdir.runpytest()
        result.assert_outcomes(passed=1)
