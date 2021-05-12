"""
Showcases minimal setup and usage of nuts. Nuts must be installed.

Test class to use in conjunction with `test-expanse.yaml` to display the minimal
functionality of nuts.

Subclasses NutsContext and therefore does not need network access.
"""

from typing import List, Dict, Any

import pytest
from nuts.context import NutsContext


class ExpanseContext(NutsContext):
    def general_result(self) -> List[Dict]:
        return [
            {"ship": "rocinante", "name": "naomi nagata", "role": "engineer", "origin": "belter"},
            {"ship": "rocinante", "name": "james holden", "role": "captain", "origin": "earth"},
            {"ship": "rocinante", "name": "amos burton", "role": "mechanic", "origin": "earth"},
            {"ship": "rocinante", "name": "alex kamal", "role": "pilot", "origin": "mars"},
            {"ship": "rocinante", "name": "bobbie draper", "role": "marine", "origin": "mars"},
        ]

    def transform_result(self, general_result: List[Dict]):
        return {
            "rocinante": {entry["name"]: {"role": entry["role"], "origin": entry["origin"]} for entry in general_result}
        }


CONTEXT = ExpanseContext


@pytest.fixture
def expanse(nuts_ctx: NutsContext, ship):
    """
    Helps to prepare the results for TestExpanseCrew and generates a fixture that
    provides the initialized context and the keyword with which the results should be filtered
    for a test.
    :param nuts_ctx: The context for a test with an initialized NutsContext subclass
    :param ship: the parameter from the yaml file
    :return: processed results ready to be passed on to a test
    """
    return nuts_ctx.transformed_result[ship]


class TestExpanseCrew:
    @pytest.mark.nuts("ship, name")
    def test_name(self, expanse: Dict, name):
        assert name in expanse.keys()

    @pytest.mark.nuts("ship, name, role")
    def test_role(self, expanse: Dict, name, role):
        assert expanse[name]["role"] == role

    @pytest.mark.nuts("ship, name, origin")
    def test_origin(self, expanse: Dict, name, origin):
        assert expanse[name]["origin"] == origin
