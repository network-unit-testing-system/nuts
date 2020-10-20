import pytest
from nornir_napalm.plugins.tasks import napalm_get


@pytest.fixture(scope="class")
def nuts_task():
    return napalm_get


@pytest.fixture(scope="class")
def nuts_arguments():
    return {"getters": ["interfaces_ip"]}


@pytest.fixture(scope="class")
def hosts(hosts_interface_list):
    return {entry["source"] for entry in hosts_interface_list}
