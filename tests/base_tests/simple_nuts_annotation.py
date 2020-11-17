import pytest


class TestKeyValue:
    @pytest.mark.nuts("key,value")
    def test_key_value(self, key, value):
        assert key == value


class TestOptionalAttribute:
    @pytest.mark.nuts("key,value", "key")
    def test_key_value(self, key, value):
        assert key == value


class TestOptionalAttributes:
    @pytest.mark.nuts("key,value", "key,value")
    def test_key_value(self, key, value):
        assert key == value
