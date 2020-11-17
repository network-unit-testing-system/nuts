import pytest


class TestKeyValue:
    @pytest.mark.nuts("key,value", "placeholder")
    def test_key_value(self, key, value):
        assert key == value


class TestNonPresentValue:
    @pytest.mark.nuts("key,value", "placeholder")
    def test_key_value(self, key, value):
        assert value is None


class TestKeyValueWithoutPlaceholder:
    @pytest.mark.nuts("key,value")
    def test_key_value(self, key, value):
        assert key == value


class TestRequiredAttribute:
    @pytest.mark.nuts("key,value", "placeholder", "value")
    def test_key_value(self, key, value):
        assert key == value


class TestRequiredAttributes:
    @pytest.mark.nuts("key,value", "placeholder", "key,value")
    def test_key_value(self, key, value):
        assert key == value
