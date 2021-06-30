"""
Showcases minimal setup and usage of nuts. Nuts must be installed.

Test class to use in conjunction with `test-expanse.yaml` to display the minimal
functionality of nuts.

Subclasses NutsContext and therefore does not need network access.
"""

from nuts.helpers.result import NutsResult, AbstractResultExtractor
from typing import List, Dict, Any

import pytest
from nuts.context import NutsContext

E = Dict[str, Dict[str, str]]


class ExpanseExtractor(AbstractResultExtractor):
    def transform_result(
        self, general_result: List[Dict[str, str]]
    ) -> Dict[str, NutsResult]:
        return {
            "rocinante": NutsResult(
                {
                    entry["name"]: {"role": entry["role"], "origin": entry["origin"]}
                    for entry in general_result
                }
            ),
        }

    def single_result(self, nuts_test_entry: Dict[str, Any]) -> NutsResult:
        ship = nuts_test_entry["ship"]
        return self.transformed_result[ship]


class ExpanseContext(NutsContext):
    def general_result(self) -> List[Dict[str, str]]:
        return [
            {
                "ship": "rocinante",
                "name": "naomi nagata",
                "role": "engineer",
                "origin": "belter",
            },
            {
                "ship": "rocinante",
                "name": "james holden",
                "role": "captain",
                "origin": "earth",
            },
            {
                "ship": "rocinante",
                "name": "amos burton",
                "role": "mechanic",
                "origin": "earth",
            },
            {
                "ship": "rocinante",
                "name": "alex kamal",
                "role": "pilot",
                "origin": "mars",
            },
            {
                "ship": "rocinante",
                "name": "bobbie draper",
                "role": "marine",
                "origin": "mars",
            },
        ]

    def nuts_extractor(self) -> ExpanseExtractor:
        return ExpanseExtractor(self)


CONTEXT = ExpanseContext


class TestExpanseCrew:
    @pytest.mark.nuts("name")
    def test_name(self, single_result: NutsResult, name: str) -> None:
        assert name in single_result.result

    @pytest.mark.nuts("name, role")
    def test_role(self, single_result: NutsResult, name: str, role: str) -> None:
        assert single_result.result[name]["role"] == role

    @pytest.mark.nuts("name, origin")
    def test_origin(self, single_result: NutsResult, name: str, origin: str) -> None:
        assert single_result.result[name]["origin"] == origin
