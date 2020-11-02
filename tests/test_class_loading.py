def test_load_class_and_execute_tests(testdir):
    arguments = {
        'test_class_loading':
            """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestClass
              arguments: []
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=2)


def test_load_class_multiple_times(testdir):
    arguments = {
        'test_class_loading':
            """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestClass
              arguments: []
            - test_module: tests.base_tests.class_loading
              test_class: TestClass
              arguments: []
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=4)


def test_injects_arguments_as_fixture(testdir):
    arguments = {
        'test_class_loading':
            """
            ---
            - test_module: tests.base_tests.class_loading
              test_class: TestFixture
              arguments: ['test1', 'test2']
            """
    }
    testdir.makefile('.yaml', **arguments)

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
