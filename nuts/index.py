"""Allows to indicate only the test class in a test bundle."""
from typing import Dict, Optional


class ModuleIndex:
    """Map a test class to the name of its module.

    Test definitions use this mapping to directly access a test
    by using the name of a test class instead of the module name.
    """

    def __init__(self, index: Dict[str, str] = None):
        """Create a new ModuleIndex.

        If None is specified the default values are taken.

        :param index: A dictionary which maps class names to modules.
                        If None is specified the default values are taken
        """
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

        self.index = index if index is not None else default_index

    def find_test_module_of_class(self, name: str) -> Optional[str]:
        """
        Try to resolve the name of the test class to a module.

        :param name: The name of the test class.
        :return: The path of the module which contains the test class.
        """
        return self.index.get(name)
