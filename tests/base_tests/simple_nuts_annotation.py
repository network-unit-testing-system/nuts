import pytest


class TestKeyValue:

    @pytest.mark.nuts("key,value", "placeholder")
    def test_key_value(self, key, value):
        assert key == value


class TestKeyValueWithoutParameter:

    @pytest.mark.nuts("key,value")
    def test_key_value(self, key, value):
        assert key == value


