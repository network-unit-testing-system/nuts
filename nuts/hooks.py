from pytest import FixtureRequest
from nuts.context import NutsContext
from nuts.helpers.result import NutsResult


def pytest_nuts_single_result(
    request: FixtureRequest, nuts_ctx: NutsContext, result: NutsResult
) -> None:
    """Called in the single result fixture"""
