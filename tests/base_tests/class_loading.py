"""
Classes in this file are needed in integration test in test_class_loading.py
"""


class TestClass:
    def test_always_true(self):
        assert True

    def test_another_assertion(self):
        assert True


class TestFixture:
    def test_nuts_parameters_correctly_injected(self, nuts_ctx):
        assert nuts_ctx.nuts_parameters["test_data"] == ["test1", "test2"]


class TestTestExecutionParamsEmpty:
    def test_nuts_test_execution(selfs, nuts_ctx):
        assert nuts_ctx.nuts_arguments() == {}


class TestTestExecutionParamsExist:
    def test_nuts_test_execution(selfs, nuts_ctx):
        assert nuts_ctx.nuts_arguments() == {"count": 42, "ref": 23}
