"""
Helper module with data used by all tests.
"""
from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"


def create_multi_result(result_content):
    multi_result = MultiResult("napalm_get")
    single_result = Result(host=None, name="napalm_get")
    single_result.result = result_content
    multi_result.append(single_result)
    return multi_result
