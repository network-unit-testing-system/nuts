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

    @pytest.fixture(scope="class")
    def nuts_arguments(self, nuts_parameters):
        return {
            "destinations_per_host": _destinations_per_host(nuts_parameters["test_data"]),
            # **nuts_parameters["test_execution"],
        }

    @pytest.fixture(scope="class")
    def general_result(self, nuts_setup_teardown, initialized_nornir, nuts_task, nuts_arguments, nornir_filter):
        if nornir_filter:
            selected_hosts = initialized_nornir.filter(nornir_filter)
        else:
            selected_hosts = initialized_nornir
        overall_results = selected_hosts.run(task=nuts_task, **nuts_arguments)
        return overall_results


    @pytest.fixture(scope="class")
    def hosts(self, nuts_parameters):
        return {entry["host"] for entry in nuts_parameters["test_data"]}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result, nuts_parameters):
        return transform_result(general_result, nuts_parameters["test_data"])

    @pytest.fixture
    def single_result(selfself, transformed_result, host):
        assert host in transformed_result, f"Host {host} not found in aggregated result."
        return transformed_result[host]

    @pytest.mark.nuts("host,destination,min_expected")
    def test_iperf(self, single_result, host, destination, min_expected):
        assert single_result


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
        # result[0].destination = destination
    return Result(host=task.host, result=f"iperf executed for {task.host}")


def transform_result(general_result, test_data) -> Dict[str, Dict[str, NutsResult]]:
    return {host: _parse_iperf_result(task_results, test_data) for host, task_results in general_result.items()}


def _parse_iperf_result(str, task_results: MultiResult, test_data: List[dict]):
    min_bps_per_destination = {
        entry["destination"]: entry["min_expected"] for entry in test_data
    }
    results_per_hosts = {}
    for iperf_task in task_results[1]:
        iperf_result = json.loads(iperf_task.result)
        results_per_hosts[iperf_result["start"]["connected"]["remoste_host"]] = iperf_result["end"]["sum_received"]["bits_per_second"]

    # TODO
    return {
        json.loads(iperf_task.result)

        for iperf_task in task_results[1:]
    }
        # nuts_result_wrapper(result, _transform_single_result)
        # response['end']['sum_received']['bits_per_second']


def destinations(test_data):
    return {entry["destination"] for entry in test_data}


def server_setup(task: Task):
    return task.run(task=netmiko_send_command, command_string=f"iperf3 --server --daemon --one-off")


def server_teardown(task: Task):
    task.run(
        task=netmiko_send_command,
        command_string=f"pkill iperf3",
    )