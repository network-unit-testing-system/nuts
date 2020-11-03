import pytest
from nornir_netmiko import netmiko_send_command


@pytest.fixture(scope="class")
def nuts_task():
    return netmiko_send_command


@pytest.fixture(scope="class")
def nuts_arguments():
    return {"command_string": "show cdp neighbors detail",
            "use_textfsm": True}


@pytest.fixture(scope="class")
def hosts(destination_list):
    return {entry["source"] for entry in destination_list}


@pytest.fixture(scope="class")
def transformed_result(general_result):
    return {source: result[0].result for source, result in general_result.items()}


@pytest.fixture(scope="class")
def grouped_result(transformed_result):
    return {source: {neighbor['destination_host']: neighbor for neighbor in neighbors} for source, neighbors in
            transformed_result.items()}
