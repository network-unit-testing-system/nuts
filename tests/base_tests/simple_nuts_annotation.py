"""
Classes in this file are needed in integration test in test_nuts_annotation.py
"""

from nuts.helpers.result import NutsResult, AbstractResultExtractor
from typing import Any, Dict
from nuts.context import NutsContext
import pytest


class FakeExtractor(AbstractResultExtractor):
    def single_result(self, nuts_test_entry: Dict[str, Any]) -> NutsResult:
        return NutsResult({})


class FakeContext(NutsContext):
    def nuts_extractor(self) -> AbstractResultExtractor:
        return FakeExtractor(self)


CONTEXT = FakeContext


class TestKeyValue:
    @pytest.mark.nuts("key,value")
    def test_key_value(self, single_result, key, value):
        assert key == value


class TestSpacedKeyValue:
    @pytest.mark.nuts(" key , value")
    def test_key_value(self, single_result, key, value):
        assert key == value


class TestOptionalAttribute:
    @pytest.mark.nuts("key,value", "key")
    def test_key_value(self, single_result, key, value):
        assert key == value


class TestOptionalAttributes:
    @pytest.mark.nuts("key,value", "key,value")
    def test_key_value(self, single_result, key, value):
        assert key == value


class TestSingleValue:
    @pytest.mark.nuts("value")
    def test_key_value(self, single_result, value):
        assert value == "test"
