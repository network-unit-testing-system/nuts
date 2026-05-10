"""Query CDP neighbors of a device."""

from typing import Callable, Dict, Any

import pytest
from nornir.core.task import MultiResult, Result
from nornir_netmiko import netmiko_send_command

from nuts.helpers.result import AbstractHostResultExtractor, NutsResult
from nuts.context import NornirNutsContext

NEIGHBOR_NAME_KEYS = {"neighbor_name", "destination_host"}
LOCAL_INTERFACE_KEYS = {"local_interface", "local_port"}
NEIGHBOR_INTERFACE_KEYS = {"neighbor_interface", "remote_port"}
MGMT_ADDRESS_KEYS = {"mgmt_address", "management_ip"}


def _extract_key(keys: set[str], entry: Dict[str, Any]) -> str:
    for key in keys:
        if key in entry:
            return entry[key]
    raise KeyError(f"None of the keys {keys} found in entry {entry}")


class CdpNeighborsExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        neighbors = self._simple_extract(single_result)
        return {
            _extract_key(NEIGHBOR_NAME_KEYS, neighbor): neighbor
            for neighbor in neighbors
        }


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
        assert remote_host in single_result.result

    @pytest.mark.nuts("remote_host,local_port")
    def test_local_port(
        self, single_result: NutsResult, remote_host: str, local_port: str
    ) -> None:
        assert (
            _extract_key(LOCAL_INTERFACE_KEYS, single_result.result[remote_host])
            == local_port
        )

    @pytest.mark.nuts("remote_host,remote_port")
    def test_remote_port(
        self, single_result: NutsResult, remote_host: str, remote_port: str
    ) -> None:
        assert (
            _extract_key(NEIGHBOR_INTERFACE_KEYS, single_result.result[remote_host])
            == remote_port
        )

    @pytest.mark.nuts("remote_host,management_ip")
    def test_management_ip(
        self, single_result: NutsResult, remote_host: str, management_ip: str
    ) -> None:
        assert (
            _extract_key(MGMT_ADDRESS_KEYS, single_result.result[remote_host])
            == management_ip
        )


class TestNetmikoCdpNeighborsCount:
    @pytest.mark.nuts("neighbor_count")
    def test_neighbor_count(self, single_result, neighbor_count):
        assert neighbor_count == len(single_result.result)
