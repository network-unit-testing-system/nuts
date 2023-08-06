import pytest
from nornir.core.filter import F, OR

from nuts.helpers.filters import filter_hosts, get_filter_object


@pytest.mark.parametrize(
    "test_data, expected",
    [
        ([{"host": "R1"}, {"host": "R2"}], ["R1", "R2"]),
        ([{"host": "R1"}, {"host": "R1"}], ["R1"]),
    ],
)
def test_filter_host(test_data, expected):
    hosts = filter_hosts(test_data).filters["name__any"]
    assert sorted(hosts) == sorted(expected)


@pytest.mark.parametrize(
    "test_data, expected",
    [
        ({"host": "R1"}, F(name__any=["R1"])),
        ({"host": ["R1", "R2"]}, F(name__any=["R1", "R2"])),
        (
            {"host": "R1", "tags": "router"},
            OR(F(name__any=["R1"]), F(tags__any=["router"])),
        ),
        (
            {"groups": "router", "tags": "router"},
            OR(F(tags__any=["router"]), F(groups__any=["router"])),
        ),
        (
            {"host": "R1", "groups": "router", "tags": "router"},
            OR(
                OR(F(name__any=["R1"]), F(tags__any=["router"])),
                F(groups__any=["router"]),
            ),
        ),
    ],
)
def test_get_filter_object(test_data, expected):
    # Would be nice if F_BASE objects would be comparable. Not the way we should do it.
    assert repr(get_filter_object(test_data)) == repr(expected)
