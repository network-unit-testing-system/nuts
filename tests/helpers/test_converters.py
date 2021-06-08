import pytest

from nuts.helpers.converters import InterfaceNameConverter

interface_test_data = [
    ("Gi1/0/1", "GigabitEthernet1/0/1"),
    ("Gi2/1/2", "GigabitEthernet2/1/2"),
    ("Fa1/0/1", "FastEthernet1/0/1"),
]


class TestInterfaceNameConverter:
    def test_constructor_initializes_with_default(self):
        assert InterfaceNameConverter().interface_conversion_rules is not None

    def test_constructor_initializes_with_argument(self):
        conversion_rules = {"T": "TestInterface"}
        converter = InterfaceNameConverter(conversion_rules)
        assert converter.interface_conversion_rules == conversion_rules

    @pytest.mark.parametrize("expected,interface_name", interface_test_data)
    def test_shorten_interface_name(self, interface_name, expected):
        shortened_name = InterfaceNameConverter().shorten_interface_name(interface_name)
        assert expected == shortened_name

    @pytest.mark.parametrize("interface_name,expected", interface_test_data)
    def test_expand_interface_name(self, interface_name, expected):
        expanded_name = InterfaceNameConverter().expand_interface_name(interface_name)
        assert expected == expanded_name
