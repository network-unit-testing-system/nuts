"""
Helper module with data used by all tests.
"""
from typing import Any, Optional

from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"


def create_multi_result(
    result_content: Any, failed: bool = False, exception: Optional[BaseException] = None
) -> MultiResult:
    multi_result = MultiResult("napalm_get")
    result = create_result(result_content, failed, exception)
    multi_result.append(result)
    return multi_result


def create_result(
    result_content: Any, failed: bool = False, exception: Optional[BaseException] = None, **kwargs
) -> Result:
    result = Result(host=None, name="naplam_get", **kwargs)
    result.result = result_content
    result.failed = failed
    result.exception = exception
    return result
