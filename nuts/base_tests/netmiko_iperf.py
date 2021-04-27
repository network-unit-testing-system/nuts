"""Query bandwidth performance between two devices."""
import pytest
import json
from typing import Dict, Callable, cast

from nornir.core.filter import F
from nornir.core.task import Task, Result, MultiResult, AggregatedResult
from nornir_netmiko import netmiko_send_command

from nuts.context import NornirNutsContext
from nuts.helpers.result import nuts_result_wrapper, NutsResult


class IperfContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return netmiko_run_iperf

    def nuts_arguments(self) -> dict:
        return {
            "destinations_per_host": _destinations_per_host(self.nuts_parameters["test_data"]),
        }

    def nornir_filter(self) -> F:
        hosts = {entry["host"] for entry in self.nuts_parameters["test_data"]}
        return F(name__any=hosts)

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, Dict[str, NutsResult]]:
        return {host: _parse_iperf_result(task_results) for host, task_results in general_result.items()}

    def setup(self) -> None:
        test_data = self.nuts_parameters["test_data"]
        destinations = F(hostname__any={entry["destination"] for entry in test_data})
        assert self.nornir is not None
        selected_destinations = self.nornir.filter(destinations)
        selected_destinations.run(task=server_setup)

    def teardown(self) -> None:
        test_data = self.nuts_parameters["test_data"]
        destinations = F(hostname__any={entry["destination"] for entry in test_data})
        assert self.nornir is not None
        selected_destinations = self.nornir.filter(destinations)
        selected_destinations.run(task=server_teardown)


CONTEXT = IperfContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoIperf:
    @pytest.fixture
    def single_result(self, nornir_nuts_ctx, host, destination):
        result = nornir_nuts_ctx.transformed_result()
        assert host in result, f"Host {host} not found in aggregated result."
        assert destination in result[host], f"Destination {destination} not found in result."
        return result[host][destination]

    @pytest.mark.nuts("host,destination,min_expected")
    def test_iperf(self, single_result, min_expected):
        assert single_result.result > min_expected


def _destinations_per_host(test_data) -> Callable:
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


def _parse_iperf_result(task_results: MultiResult) -> Dict[str, NutsResult]:
    results_per_host = {}
    for elem in task_results[1:]:
        iperf_task = cast(MultiResult, elem)  # mypy: Even if it's of type Result, treat it as Multiresult
        # allows a MultiResult to contain other MultiResults
        results_per_host[_extract_dest(iperf_task[1])] = nuts_result_wrapper(iperf_task[1], _extract_bps)
    return results_per_host


def _extract_bps(iperf_task) -> int:
    iperf_result = json.loads(iperf_task.result)
    return int(iperf_result["end"]["sum_received"]["bits_per_second"])


def _extract_dest(iperf_task) -> str:
    iperf_result = json.loads(iperf_task.result)
    return iperf_result["start"]["connected"][0]["remote_host"]


def server_setup(task: Task) -> None:
    task.run(task=netmiko_send_command, command_string=f"iperf3 --server --daemon")


def server_teardown(task: Task) -> None:
    task.run(
        task=netmiko_send_command,
        command_string=f"pkill iperf3",
    )
