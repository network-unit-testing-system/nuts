import pytest


class TestKeyValue:
    """Needed in integration test in test_nuts_annotation.py"""

    @pytest.mark.nuts("key,value")
    def test_key_value(self, key, value):
        assert key == value


class TestSpacedKeyValue:
    """Needed in integration test in test_nuts_annotation.py"""

    @pytest.mark.nuts(" key , value")
    def test_key_value(self, key, value):
        assert key == value


class TestOptionalAttribute:
    """Needed in integration test in test_nuts_annotation.py"""

    @pytest.mark.nuts("key,value", "key")
    def test_key_value(self, key, value):
        assert key == value


class TestOptionalAttributes:
    """Needed in integration test in test_nuts_annotation.py"""

    @pytest.mark.nuts("key,value", "key,value")
    def test_key_value(self, key, value):
        assert key == value
