"""
Helper module with data used by all tests.
"""

from dataclasses import dataclass
from typing import Any, Optional, List, Dict

from nornir.core.inventory import Host
from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"


@dataclass
class SelfTestData:
    """
    Helper-Class that matches raw nornir results with a test data entry.
    One instance of SelfTestData corresponds to one self-test case.

    There are two possible ways to construct a SelfTestData object:
        1) 1 raw nornir result contains data that is related to several
            test_data entries
        2) 1 raw nornir result contains data that related to exactly one test_data entry

        For 1), several instances of this class have to be created containing the same
        raw nornir results but different test data entries.
    :param name: identifier of the test case so that it can be easily identified
        in parametrized tests.
    :param nornir_raw_result: mocked raw answer from nornir
    :param test_data: expected results for the test case
    :param additional_data: data that is provided by nornir
        but not used in a nuts base test
    :param expected_output: list of strings that is matched against
        pytest's output using fnmatch globs
    :param expected_outcome: values of possible pytest outcomes
        (e.g. 'failed', 'errors'), default is 'passed'
    """

    name: str
    nornir_raw_result: Any
    test_data: Dict[str, Any]
    additional_data: Optional[Dict[str, Any]] = None
    expected_output: Optional[List[str]] = None
    expected_outcome: str = "passed"

    def create_nornir_result(self) -> Result:
        return create_result(
            result_content=self.nornir_raw_result,
            host=self.test_data["host"],
            destination=self.test_data.get("destination", None),
        )


def create_multi_result(results: List[Result], task_name: str) -> MultiResult:
    multi_result = MultiResult(task_name)
    multi_result += results
    return multi_result


def create_result(
    result_content: Any,
    host: str = "",
    destination: Optional[str] = None,
    failed: bool = False,
    exception: Optional[BaseException] = None,
    **kwargs: Any
) -> Result:
    result = Result(host=Host(name=host), destination=destination, **kwargs)
    result.result = result_content
    result.failed = failed
    result.exception = exception
    return result
