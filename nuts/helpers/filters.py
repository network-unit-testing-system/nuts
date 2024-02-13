"""
Functions to filter the nornir inventory and used in conjunction with
a context's nornir_filter function.
"""

from typing import Optional, Dict, Any, List, Union
from nornir.core.filter import F, OR

from nuts.helpers.errors import NutsSetupError


def filter_hosts(test_data: Optional[List[Dict[str, Any]]]) -> F:
    assert test_data is not None
    hosts: List[str] = list({entry["host"] for entry in test_data})
    return F(name__any=hosts)


def get_filter_object(test_data_entry: Dict[str, Any]) -> Union[F, OR]:
    """
    Create Nornir filter object. Supported test_data fields are:
    - "host:"
    - "tags:"
    - "groups:"

    :param test_data (List[Dict[str, Any]]): Test data from YAML

    :raises NutsSetupError: if no filter could be build (missing fields)

    :return: Nornir filter object
    """
    filters: List[F] = []
    properties: Dict[str, str] = {"name": "host", "tags": "tags", "groups": "groups"}
    for inventory_property, test_data_property in properties.items():
        if test_data_property in test_data_entry:
            filter_data = test_data_entry[test_data_property]
            if not isinstance(filter_data, list):
                filter_data = [filter_data]

            filters.append(F(**{f"{inventory_property}__any": filter_data}))

    if len(filters) == 0:
        raise NutsSetupError(
            "No Nornir filter could be created. "
            "Check if `host`, `tags` or `groups` are specified."
        )
    elif len(filters) == 1:
        return filters[0]
    else:
        or_filter = OR(filters[0], filters[1])
        for f in filters[2:]:
            or_filter = OR(or_filter, f)

        return or_filter
