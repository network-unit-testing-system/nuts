import pytest


class TestKeyValue:
    @pytest.mark.nuts("key,value", "placeholder")
    def test_key_value(self, key, value):
        assert key == value


class TestKeyValueWithoutPlaceholder:
    @pytest.mark.nuts("key,value")
    def test_key_value(self, key, value):
        assert key == value


class TestOptionalAttribute:
    @pytest.mark.nuts("key,value", "placeholder", "key")
    def test_key_value(self, key, value):
        assert key == value


class TestOptionalAttributes:
    @pytest.mark.nuts("key,value", "placeholder", "key,value")
    def test_key_value(self, key, value):
        assert key == value
