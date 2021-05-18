"""
Helper module with data used by all tests.
"""
from dataclasses import dataclass
from typing import Any, Optional, List, Dict, Tuple

from nornir.core.inventory import Host
from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"


@dataclass
class SelfTestData:
    """
    Helper-Class that pairs the raw result that is sent over the wire with the test data (expected values).
    """

    nornir_raw_result: Any
    test_data: Dict[str, Any]

    def create_nornir_result(self, task_name: str) -> Result:
        return create_result(
            result_content=self.nornir_raw_result,
            task_name=task_name,
            host=self.test_data["host"],
            destination=self.test_data.get("destination", None),
        )


def create_multi_result(results: List[Result], task_name: str) -> MultiResult:
    multi_result = MultiResult(task_name)
    multi_result += results
    return multi_result


def create_result(
    result_content: Any,
    task_name: str,
    host: str = "",
    destination: Optional[str] = None,
    failed: bool = False,
    exception: Optional[BaseException] = None,
    **kwargs: Any
) -> Result:
    result = Result(host=Host(name=host), name=task_name, destination=destination, **kwargs)
    result.result = result_content
    result.failed = failed
    result.exception = exception
    return result


def tupelize(source: Dict[str, Any], fields: List[str]) -> Tuple[Optional[Any], ...]:
    ordered_fields = [source.get(field) for field in fields]
    return tuple(ordered_fields)
