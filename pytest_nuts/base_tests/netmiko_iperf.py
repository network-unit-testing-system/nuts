import pytest
import json
from typing import Dict, List

from nornir.core.filter import F
from nornir.core.task import Task, Result, MultiResult
from nornir_netmiko import netmiko_send_command

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult


class TestNetmikoIperf:

    @pytest.fixture(scope="class")
    def nuts_setup_teardown(self, nuts_parameters, initialized_nornir):
        selected_destinations = initialized_nornir.filter(F(hostname__any=destinations(nuts_parameters["test_data"])))
        selected_destinations.run(task=server_setup)
        yield None
        selected_destinations.run(task=server_teardown)

    @pytest.fixture(scope="class")
    def nuts_task(self):
        return netmiko_run_iperf

    @pytest.fixture(scope="class")
    def nornir_filter(self, hosts):
        return F(name__any=hosts)

    # TODO duplicate to Ping
    @pytest.fixture(scope="class")
    def nuts_arguments(self, nuts_parameters):
        return {
            "destinations_per_host": _destinations_per_host(nuts_parameters["test_data"]),
            # **nuts_parameters["test_execution"],
        }

    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["host"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result, nuts_parameters):
        return transform_result(general_result, nuts_parameters["test_data"])

    @pytest.mark.nuts("host,destination,min_expected")
    def test_iperf(self, general_result, host, destination, min_expected):
        assert general_result


# TODO duplicate to Ping - move to helper?
def _destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["host"] == host_name]


def _client_iperf(task: Task, dest: str):
    task.run(
        task=netmiko_send_command,
        command_string=f"iperf3 -c {dest} --json",
    )


def netmiko_run_iperf(task: Task, destinations_per_host, **kwargs) -> Result:
    dests = destinations_per_host(task.host.name)
    for destination in dests:
        result = task.run(task=_client_iperf, dest=destination, **kwargs)
        result[0].destination = destination
    return Result(host=task.host, result=f"iperf executed for {task.host}")


def transform_result(general_result, test_data) -> Dict[str, Dict[str, NutsResult]]:
    return {host: task_results for host, task_results in general_result.items()}


def destinations(test_data):
    return {entry["destination"] for entry in test_data}


def server_setup(task: Task):
    return task.run(task=netmiko_send_command, command_string=f"iperf3 --server --daemon --one-off")


def server_teardown(task: Task):
    task.run(
        task=netmiko_send_command,
        command_string=f"pkill iperf3",
    )