import pytest


@pytest.fixture(scope="class")
def param1():
    return "Param1"


class TestModuleLevelFixture:
    def test_key_value(self, param1):
        assert True
