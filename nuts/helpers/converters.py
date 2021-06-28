from typing import Dict, Optional


class InterfaceNameConverter:
    def __init__(self, conversion_rules: Optional[Dict[str, str]] = None):
        self.interface_conversion_rules = conversion_rules or {
            "GigabitEthernet": "Gi",
            "FastEthernet": "Fa",
        }

    def shorten_interface_name(self, name: str) -> str:
        for key, value in self.interface_conversion_rules.items():
            if name.lower().startswith(key.lower()):
                return value + name[len(key) :]  # noqa: E203
        return name

    def expand_interface_name(self, name: str) -> str:
        for key, value in self.interface_conversion_rules.items():
            if name.lower().startswith(value.lower()):
                return key + name[len(value) :]  # noqa: E203
        return name
