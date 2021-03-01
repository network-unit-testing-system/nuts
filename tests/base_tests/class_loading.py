class TestClass:
    """ Needed in integration test in test_class_loading.py"""

    def test_always_true(self):
        assert True

    def test_another_assertion(self):
        assert True


class TestFixture:
    """ Needed in integration test in test_class_loading.py"""

    def test_always_true(self, nuts_ctx):
        assert nuts_ctx.nuts_parameters["test_data"] == ["test1", "test2"]

