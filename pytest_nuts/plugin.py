import pytest
from nornir import InitNornir


@pytest.fixture(scope="session")
def nornir_config_file():
    return "nr-config.yaml"


@pytest.fixture(scope="class")
def nuts_arguments():
    return {}


@pytest.fixture(scope="class")
def nornir_filter():
    return None


@pytest.fixture(scope="session")
def nr(nornir_config_file):
    return InitNornir(config_file=nornir_config_file,
                      logging=False)


@pytest.fixture(scope="class")
def general_result(nr, nuts_task, nuts_arguments, nornir_filter):
    if nornir_filter:
        selected_hosts = nr.filter(nornir_filter)
    else:
        selected_hosts = nr
    overall_results = selected_hosts.run(task=nuts_task, **nuts_arguments)
    return overall_results
