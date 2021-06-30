"""Query bandwidth performance between two devices."""
import pytest
import json
from typing import Dict, Callable, Any
import shlex

from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_netmiko import netmiko_send_command

from nuts.context import NornirNutsContext
from nuts.helpers.filters import filter_hosts
from nuts.helpers.errors import Error
from nuts.helpers.result import NutsResult, AbstractHostDestResultExtractor


class IperfExtractor(AbstractHostDestResultExtractor):
    def single_transform(self, single_result: Result) -> int:
        assert isinstance(single_result.result, str)
        return self._extract_bps(single_result.result)

    def _extract_bps(self, iperf_task_result: str) -> int:
        iperf_result = json.loads(iperf_task_result)
        if "error" in iperf_result:
            raise IperfResultError(iperf_result["error"])
        return int(iperf_result["end"]["sum_received"]["bits_per_second"])

    def single_result(self, nuts_test_entry: Dict[str, Any]) -> NutsResult:
        host = nuts_test_entry["host"]
        destination = nuts_test_entry["destination"]
        assert (
            host in self.transformed_result
        ), f"Host {host} not found in aggregated result."
        assert (
            destination in self.transformed_result[host]
        ), f"Destination {destination} not found in result."
        return self.transformed_result[host][destination]


class IperfContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return self.netmiko_run_iperf

    def netmiko_run_iperf(self, task: Task) -> Result:
        """
        Runs iperf between a host and several destinations.
        During setup, the destinations have been set up
        to act as servers.

        Note: The destination is not included in the nornir result
        if the iperf test fails. Therefore we cannot know which destination
        was not reachable, so we must patch the destination
        onto the result object to know later
        which host-destination pair actually failed.

        :param task: nornir task for iperf
        :return: All iperf results per host
        """
        destinations_per_host = [
            entry["destination"]
            for entry in self.nuts_parameters["test_data"]
            if entry["host"] == task.host.name
        ]
        for destination in destinations_per_host:
            escaped_dest = shlex.quote(destination)
            result = task.run(
                task=netmiko_send_command,
                command_string=f"iperf3 -c {escaped_dest} --json",
            )
            result[0].destination = destination  # type: ignore[attr-defined]
        return Result(host=task.host, result=f"iperf executed for {task.host}")

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def setup(self) -> None:
        """
        Sets up the all destinations to act as iperf servers.
        """
        test_data = self.nuts_parameters["test_data"]
        destinations = F(hostname__any={entry["destination"] for entry in test_data})
        assert self.nornir is not None
        selected_destinations = self.nornir.filter(destinations)
        selected_destinations.run(task=self.server_setup)

    def server_setup(self, task: Task) -> None:
        task.run(task=netmiko_send_command, command_string="iperf3 --server --daemon")

    def teardown(self) -> None:
        """
        Stops all destinations that acted as iperf servers.
        """
        test_data = self.nuts_parameters["test_data"]
        destinations = F(hostname__any={entry["destination"] for entry in test_data})
        assert self.nornir is not None
        selected_destinations = self.nornir.filter(destinations)
        selected_destinations.run(task=self.server_teardown)

    def server_teardown(self, task: Task) -> None:
        task.run(
            task=netmiko_send_command,
            command_string="pkill iperf3",
        )

    def nuts_extractor(self) -> IperfExtractor:
        return IperfExtractor(self)


CONTEXT = IperfContext


class IperfResultError(Error):

    """Error in iperf result JSON."""


class TestNetmikoIperf:
    @pytest.mark.nuts("min_expected")
    def test_iperf(self, single_result, min_expected):
        assert single_result.result >= min_expected
