"""
Helper module with data used by all tests.
"""
from nornir.core.task import MultiResult, Result

YAML_EXTENSION = ".yaml"


def create_multi_result(result_content):
    multi_result_r1 = MultiResult("napalm_get")
    result_r1 = Result(host=None, name="naplam_get")
    result_r1.result = result_content
    multi_result_r1.append(result_r1)
    return multi_result_r1
