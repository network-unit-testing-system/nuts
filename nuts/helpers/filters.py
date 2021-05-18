"""
Functions to filter the nornir inventory and used in conjunction with
a context's nornir_filter function.
"""
from typing import Optional, Dict, Any, List, Set

from nornir.core.filter import F


def filter_hosts(test_data: Optional[List[Dict[str, Any]]]) -> F:
    assert test_data is not None
    hosts: Set[str] = {entry["host"] for entry in test_data}
    return F(name__any=hosts)
