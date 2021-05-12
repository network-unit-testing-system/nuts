"""Query bandwidth performance between two devices."""
import pytest
import json
from typing import Dict, Callable
import shlex

from nornir.core.filter import F
from nornir.core.task import Task, Result, AggregatedResult
from nornir_netmiko import netmiko_send_command

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import NutsResult, map_host_to_dest_to_nutsresult


class IperfContext(NornirNutsContext):
    def nuts_task(self) -> Callable:
        return self.netmiko_run_iperf

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, Dict[str, NutsResult]]:
        return map_host_to_dest_to_nutsresult(general_result, self._transform_single_entry)

    def _transform_single_entry(self, single_result: Result) -> int:
        assert isinstance(single_result.result, str)
        return _extract_bps(single_result.result)

    def netmiko_run_iperf(self, task: Task) -> Result:
        """
        Runs iperf between a host and several destinations. During setup, the destinations have been set up
        to act as servers.

        Note: The destination is not included in the nornir result if the iperf test fails.
        Therefore we cannot know which destination was not reachable,
        so we must patch the destination onto the result object to know later which
        host-destination pair actually failed.

        :param task: nornir task for iperf
        :return: All iperf results per host
        """
        destinations_per_host = [
            entry["destination"] for entry in self.nuts_parameters["test_data"] if entry["host"] == task.host.name
        ]
        for destination in destinations_per_host:
            escaped_dest = shlex.quote(destination)
            result = task.run(task=netmiko_send_command, command_string=f"iperf3 -c {escaped_dest} --json")
            result[0].destination = destination  # type: ignore[attr-defined]
        return Result(host=task.host, result=f"iperf executed for {task.host}")

    def setup(self) -> None:
        """
        Sets up the all destinations to act as iperf servers.
        """
        test_data = self.nuts_parameters["test_data"]
        destinations = F(hostname__any={entry["destination"] for entry in test_data})
        assert self.nornir is not None
        selected_destinations = self.nornir.filter(destinations)
        selected_destinations.run(task=server_setup)

    def teardown(self) -> None:
        """
        Stops all destinations that acted as iperf servers.
        """
        test_data = self.nuts_parameters["test_data"]
        destinations = F(hostname__any={entry["destination"] for entry in test_data})
        assert self.nornir is not None
        selected_destinations = self.nornir.filter(destinations)
        selected_destinations.run(task=server_teardown)


CONTEXT = IperfContext


@pytest.mark.usefixtures("check_nuts_result")
class TestNetmikoIperf:
    @pytest.fixture
    def single_result(self, nuts_ctx: NornirNutsContext, host, destination):
        assert host in nuts_ctx.transformed_result, f"Host {host} not found in aggregated result."
        assert destination in nuts_ctx.transformed_result[host], f"Destination {destination} not found in result."
        return nuts_ctx.transformed_result[host][destination]

    @pytest.mark.nuts("host,destination,min_expected")
    def test_iperf(self, single_result, min_expected):
        assert single_result.result > min_expected


def _extract_bps(iperf_task_result: str) -> int:
    iperf_result = json.loads(iperf_task_result)
    if "error" in iperf_result:
        raise Exception(iperf_result["error"])
    return int(iperf_result["end"]["sum_received"]["bits_per_second"])


def server_setup(task: Task) -> None:
    task.run(task=netmiko_send_command, command_string="iperf3 --server --daemon")


def server_teardown(task: Task) -> None:
    task.run(
        task=netmiko_send_command,
        command_string="pkill iperf3",
    )
