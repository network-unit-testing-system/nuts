"""
Helper module with data used by all tests.
"""
from typing import Any, Optional

from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"


def create_multi_result(
    result_content: Any, failed: Optional[bool] = False, exception: Optional[BaseException] = None
) -> MultiResult:
    multi_result = MultiResult("napalm_get")
    result = Result(host=None, name="naplam_get")
    result.result = result_content
    result.failed = failed
    result.exception = exception
    multi_result.append(result)
    return multi_result
