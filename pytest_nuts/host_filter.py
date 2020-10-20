import pytest
from nornir.core.filter import F


@pytest.fixture(scope="class")
def nornir_filter(hosts):
    return F(name__any=hosts)
