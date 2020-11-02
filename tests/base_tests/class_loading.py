class TestClass:

    def test_always_true(self):
        assert True

    def test_another_assertion(self):
        assert True


class TestFixture:

    def test_always_true(self, nuts_parameters):
        assert nuts_parameters == {'arguments': ['test1', 'test2']}
