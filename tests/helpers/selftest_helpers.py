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
    Helper-Class that matches raw nornir results with a test data entry.
    There are two possible structures:
        1) 1 raw nornir results contains data that matches several test data entries
        2) 1 raw nornir result contains data that matches exactly one test data entry

        For 1), several instances of this class have to be created containing the same
        raw nornir results but different test data entries.
    """

    nornir_raw_result: Any
    test_data: Dict[str, Any]
    additional_data: Optional[Dict[str, Any]] = None

    def create_nornir_result(self, task_name: str):
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
    **kwargs
) -> Result:
    result = Result(host=Host(name=host), name=task_name, destination=destination, **kwargs)
    result.result = result_content
    result.failed = failed
    result.exception = exception
    return result
