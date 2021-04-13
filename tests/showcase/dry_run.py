__path__ = "tests.showcase.dry_run.TestExpanseCrew"

from typing import List, Dict, Any

import pytest
from pytest_nuts.context import NutsContext


class ExpanseContext(NutsContext):

    def __init__(self, nuts_parameters: Any = None):
        super().__init__(nuts_parameters)

    def general_result(self) -> List[Dict]:
        return [{'host': 'rocinante', 'name': 'naomi_nagata', 'role': 'engineer', 'origin': 'belter'}, {'host': 'rocinante', 'name': 'james_holden', 'role': 'captain', 'origin': 'earth'}, {'host': 'rocinante', 'name': 'amos_burton', 'role': 'mechanic', 'origin': 'earth'}, {'host': 'rocinante', 'name': 'alex_kamal', 'role': 'pilot', 'origin': 'mars'}, {'host': 'rocinante', 'name': 'bobbie_draper', 'role': 'marine', 'origin': 'mars'}]

    def transform_result(self, general_result: List[Dict]):
        return {
            "rocinante": { entry["name"]: {"role": entry["role"], "origin": entry["origin"]} for entry in general_result}
        }

    def transformed_result(self):
        return self.transform_result(self.general_result())

CONTEXT = ExpanseContext


class TestExpanseCrew:
    @pytest.mark.nuts("host,name")
    def test_name(self, single_result: Dict, name):
        assert name in single_result.keys()

    @pytest.mark.nuts("host, name, role")
    def test_role(self, single_result: Dict, name, role):
        assert single_result[name]["role"] == role

    @pytest.mark.nuts("host, name, origin")
    def test_origin(self, single_result: Dict, name, origin):
        assert single_result[name]["origin"] == origin