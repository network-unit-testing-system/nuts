"""
Helper module with data used by all tests.
"""
from typing import Any, Optional, List

from nornir.core.inventory import Host
from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"


def create_multi_result(results: List[Result], task_name: str) -> MultiResult:
    multi_result = MultiResult(task_name)
    for result in results:
        multi_result.append(result)
    return multi_result


def create_result(
    result_content: Any,
    task_name: str,
    host: str = "",
    destination: Optional[str] = None,
    failed: bool = False,
    exception: Optional[BaseException] = None,
    **kwargs
) -> Result:
    result = Result(host=Host(name=host), name=task_name, destination=destination, **kwargs)
    result.result = result_content
    result.failed = failed
    result.exception = exception
    return result
