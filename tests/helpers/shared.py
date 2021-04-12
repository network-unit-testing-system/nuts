"""
Helper module with data used by all tests.
"""
from typing import Any, Optional

from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"

class Host():
    """
    Mocks nornir.core.Host class
    """
    def __init__(self, name: str):
        self.name = name

def create_multi_result(
    result_content: Any, task_name: str, host: Optional[Host]=None, failed: bool = False, exception: Optional[BaseException] = None
) -> MultiResult:
    multi_result = MultiResult(task_name)
    result = create_result(result_content, task_name, host, failed, exception)
    multi_result.append(result)
    return multi_result


def create_result(result_content: Any, task_name: str, host: Optional[Host], failed: bool = False, exception: Optional[BaseException] = None, **kwargs
) -> Result:
    result = Result(host=host, name=task_name, **kwargs)
    result.result = result_content
    result.failed = failed
    result.exception = exception
    return result
