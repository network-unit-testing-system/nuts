def test_execute_tests_based_on_arguments(testdir):
    arguments = {
        'test_class_loading':
            """
---
- test_module: tests.base_tests.simple_nuts_annotation
  test_class: TestKeyValue
  arguments: [{"key": "abc", "value":"abc"}, 
  {"key": "cde", "value":"cde"}]
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=2)


def test_skips_execution_without_arguments(testdir):
    arguments = {
        'test_class_loading':
            """
---
- test_module: tests.base_tests.simple_nuts_annotation
  test_class: TestKeyValue
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(skipped=1)


def test_execute_tests_errors_with_incomplete_data(testdir):
    arguments = {
        'test_class_loading':
            """
---
- test_module: tests.base_tests.simple_nuts_annotation
  test_class: TestKeyValue
  arguments: [{"key": "abc"}]
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(errors=1)


def test_execute_tests_multiple_times_separates_arguments(testdir):
    arguments = {
        'test_class_loading':
            """
---
- test_module: tests.base_tests.simple_nuts_annotation
  test_class: TestKeyValue
  arguments: [{"key": "abc", "value":"abc"}]
- test_module: tests.base_tests.simple_nuts_annotation
  test_class: TestKeyValue
  arguments: [{"key": "abc", "value":"bcd"}]
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=1, failed=1)


def test_execute_tests_errors_without_placeholder(testdir):
    arguments = {
        'test_class_loading':
            """
---
- test_module: tests.base_tests.simple_nuts_annotation
  test_class: TestKeyValueWithoutParameter
  arguments: [{"key": "abc", "value":"abc"}]
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(errors=1)
