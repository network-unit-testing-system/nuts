"""Query CDP neighbors of a device."""

from typing import Callable, Dict, Any

import pytest
from nornir.core.task import MultiResult, Result
from nornir_netmiko import netmiko_send_command

from nuts.helpers.result import AbstractHostResultExtractor, NutsResult
from nuts.context import NornirNutsContext


class CdpNeighborsExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        neighbors = self._simple_extract(single_result)
        return {neighbor["local_interface"]: neighbor for neighbor in neighbors}


class CdpNeighborsContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return netmiko_send_command

    def nuts_arguments(self) -> Dict[str, Any]:
        return {"command_string": "show cdp neighbors detail", "use_textfsm": True}

    def nuts_extractor(self) -> CdpNeighborsExtractor:
        return CdpNeighborsExtractor(self)


CONTEXT = CdpNeighborsContext


class TestNetmikoCdpNeighbors:
    @pytest.mark.nuts("remote_host")
    def test_remote_host(self, single_result: NutsResult, remote_host: str) -> None:
        assert any(v.get("neighbor_name") for k, v in single_result.result.items())

    @pytest.mark.nuts("remote_host,local_port")
    def test_local_port(
        self, single_result: NutsResult, remote_host: str, local_port: str
    ) -> None:
        assert single_result.result[local_port]["neighbor_name"] == remote_host

    @pytest.mark.nuts("remote_host,remote_port")
    def test_remote_port(
        self, single_result: NutsResult, remote_host: str, remote_port: str
    ) -> None:
        assert any(v.get("neighbor_name") == remote_host and v.get("neighbor_interface") == remote_port for k, v in single_result.result.items())

    @pytest.mark.nuts("remote_host,management_ip")
    def test_management_ip(
        self, single_result: NutsResult, remote_host: str, management_ip: str
    ) -> None:
        assert any(v.get("neighbor_name") == remote_host and v.get("mgmt_address") == management_ip for k, v in single_result.result.items())


class TestNetmikoCdpNeighborsCount:
    @pytest.mark.nuts("neighbor_count")
    def test_neighbor_count(self, single_result, neighbor_count):
        assert neighbor_count == len(single_result.result)
