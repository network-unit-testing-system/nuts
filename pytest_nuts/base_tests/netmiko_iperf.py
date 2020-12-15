import pytest
import json
from typing import Dict, List

from nornir.core.filter import F
from nornir.core.task import Task, Result, MultiResult
from nornir_netmiko import netmiko_send_command

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult


# TODO write Tests
# TODO write Documentation

@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoIperf:
    @pytest.fixture(scope="class")
    def nuts_task(self):
        return netmiko_run_iperf

    # TODO duplicate to Ping - move to helper?
    @pytest.fixture(scope="class")
    def nuts_arguments(self, nuts_parameters):
        return {
            "destinations_per_host": _destinations_per_host(nuts_parameters["test_data"]),
            **nuts_parameters["test_execution"],
        }

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["host"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result, nuts_parameters):
        return transform_result(general_result, nuts_parameters["test_data"])

def transform_result(general_result, test_data) -> Dict[str, Dict[str, NutsResult]]:
    pass

# TODO duplicate to Ping - move to helper?
def _destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["host"] == host_name]

def destinations(test_data):
    return lambda host_name: { entry["destination"] for entry in test_data }  # create set for uniqueness

def _server_setup(task: Task):
    return task.run(
        task=netmiko_send_command,
        command_string=f"iperf3 --server --daemon --one-off"
    )

def _client_iperf(task: Task, dest: str):
    task.run(
        task=netmiko_send_command,
        command_string=f"iperf3 -c {dest} --json",
    )

def _server_teardown(task: Task):
    task.run(
        task=netmiko_send_command,
        command_string=f"pkill iperf3",
    )

def netmiko_run_iperf(task: Task, destinations_per_host, destinations, **kwargs) -> Result:
    # setup server for all destinations
    server = nr.filter(destinations)
    server.run(task=_server_setup)

    # execute iperf on 1 client for all relevant destinations
    destinations = destinations_per_host(task.host.name)
    for destination in destinations:
        result = task.run(task=_client_iperf, dest=destination, **kwargs)
        result[0].destination = destination

    # teardown server
    server.run(task=_server_teardown)
    return Result(host=task.host, result=f"iperf for all destinations of {task.host} executed"




    # server = nr.filter(F(name__all="L2"))
    # client = nr.filter(F(name__all="L1"))
    #
    # s_res1 = server.run(task=setup_server, server_args="--one-off")
    # c_res = client.run(task=client_iperf3, destination="10.20.2.12")
    # s_res2 = server.run(task=server_teardown, destination="10.20.2.12")


    )



# teardown all destinations