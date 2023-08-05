import pytest

from nuts.yamlloader import load_module
from nuts.helpers.context import load_context

from tests.showcase.showcase_expanse import ExpanseContext


class TestContextHelper:
    def test_load_context(self):
        module = load_module("tests.showcase.showcase_expanse")

        test_data = [
            {
                "ship": "rocinante",
                "name": "naomi nagate",
                "role": "engineer",
                "origin": "belter",
            },
            {
                "ship": "rocinante",
                "name": "james holden",
                "role": "captain",
                "origin": "earth",
            },
        ]

        ctx = load_context(module, test_data)
        assert ctx.__module__ == "tests.showcase.showcase_expanse"
