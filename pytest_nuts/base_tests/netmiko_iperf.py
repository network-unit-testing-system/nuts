import pytest
import json
from typing import Dict

from nornir.core.filter import F
from nornir.core.task import Task, Result, MultiResult
from nornir_netmiko import netmiko_send_command

from pytest_nuts.helpers.result import nuts_result_wrapper, NutsResult


@pytest.mark.usefixtures("check_nuts_result")
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
    def nuts_arguments(self, nuts_parameters):
        return {
            "destinations_per_host": _destinations_per_host(nuts_parameters["test_data"]),
        }

    @pytest.fixture(scope="class")
    def nornir_filter(self, hosts):
        return F(name__any=hosts)

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
    def transformed_result(self, general_result):
        return transform_result(general_result)

    @pytest.fixture
    def single_result(self, transformed_result, host, destination):
        assert host in transformed_result, f"Host {host} not found in aggregated result."
        assert destination in transformed_result[host], f"Destination {destination} not found in result."
        return transformed_result[host][destination]

    @pytest.mark.nuts("host,destination,min_expected")
    def test_iperf(self, single_result, min_expected):
        assert single_result.result > min_expected


def _destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["host"] == host_name]


def _client_iperf(task: Task, dest: str) -> None:
    task.run(
        task=netmiko_send_command,
        command_string=f"iperf3 -c {dest} --json",
    )


def netmiko_run_iperf(task: Task, destinations_per_host) -> Result:
    dests = destinations_per_host(task.host.name)
    for destination in dests:
        task.run(task=_client_iperf, dest=destination)
    return Result(host=task.host, result=f"iperf executed for {task.host}")


def transform_result(general_result) -> Dict[str, Dict[str, NutsResult]]:
    return {host: _parse_iperf_result(task_results) for host, task_results in general_result.items()}


def _parse_iperf_result(task_results: MultiResult) -> Dict[str, NutsResult]:
    results_per_host = {}
    for iperf_task in task_results[1:]:
        results_per_host[_extract_dest(iperf_task)] = nuts_result_wrapper(iperf_task, _extract_bps)  # TODO
    return results_per_host


def _extract_bps(iperf_task):
    iperf_result = json.loads(iperf_task[1].result)
    return int(iperf_result["end"]["sum_received"]["bits_per_second"])


def _extract_dest(iperf_task):
    iperf_result = json.loads(iperf_task[1].result)
    return iperf_result["start"]["connected"][0]["remote_host"]


def destinations(test_data):
    return {entry["destination"] for entry in test_data}


def server_setup(task: Task):
    task.run(task=netmiko_send_command, command_string=f"iperf3 --server --daemon --one-off")


def server_teardown(task: Task):
    task.run(
        task=netmiko_send_command,
        command_string=f"pkill iperf3",
    )
