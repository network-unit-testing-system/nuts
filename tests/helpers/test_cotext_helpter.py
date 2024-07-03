from pytest import FixtureRequest

from nuts.yamlloader import load_module
from nuts.helpers.context import load_context


def test_load_context(request: FixtureRequest) -> None:
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

    ctx = load_context(module, test_data, request.config)
    assert ctx.__module__ == "tests.showcase.showcase_expanse"
