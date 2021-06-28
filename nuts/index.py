"""Allows to indicate only the test class name in a test bundle."""
from typing import Optional

default_index = {
    "TestNapalmBgpNeighbors": "nuts.base_tests.napalm_bgp_neighbors",
    "TestNapalmBgpNeighborsCount": "nuts.base_tests.napalm_bgp_neighbors",
    "TestNapalmInterfaces": "nuts.base_tests.napalm_interfaces",
    "TestNapalmLldpNeighbors": "nuts.base_tests.napalm_lldp_neighbors",
    "TestNapalmNetworkInstances": "nuts.base_tests.napalm_network_instances",
    "TestNapalmPing": "nuts.base_tests.napalm_ping",
    "TestNapalmUsers": "nuts.base_tests.napalm_get_users",
    "TestNetmikoCdpNeighbors": "nuts.base_tests.netmiko_cdp_neighbors",
    "TestNetmikoIperf": "nuts.base_tests.netmiko_iperf",
    "TestNetmikoOspfNeighborsCount": "nuts.base_tests.netmiko_ospf_neighbors",
    "TestNetmikoOspfNeighbors": "nuts.base_tests.netmiko_ospf_neighbors",
}


def find_test_module_of_class(name: str) -> Optional[str]:
    """
    Try to resolve the name of the test class to a module.

    Test definitions can use an index to directly access a test
    by using the name of a test class instead of the module name.


    :param name: The name of the test class.
    :return: The path of the module which contains the test class.
    """
    return default_index.get(name, None)
