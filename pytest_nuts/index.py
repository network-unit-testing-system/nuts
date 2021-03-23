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
            "TestNetmikoCdpNeighbors": "pytest_nuts.base_tests.netmiko_cdp_neighbors",
            "TestNapalmPing": "pytest_nuts.base_tests.napalm_ping",
            "TestNapalmLldpNeighbors": "pytest_nuts.base_tests.napalm_lldp_neighbors",
            "TestNetmikoOspfNeighborsCount": "pytest_nuts.base_tests.netmiko_ospf_neighbors",
            "TestNetmikoOspfNeighbors": "pytest_nuts.base_tests.netmiko_ospf_neighbors",
            "TestNapalmNetworkInstances": "pytest_nuts.base_tests.napalm_network_instances",
            "TestNapalmBgpNeighbors": "pytest_nuts.base_tests.napalm_bgp_neighbors",
            "TestNapalmBgpNeighborsCount": "pytest_nuts.base_tests.napalm_bgp_neighbors",
            "TestNapalmUsers": "pytest_nuts.base_tests.napalm_get_users",
            "TestNetmikoIperf": "pytest_nuts.base_tests.netmiko_iperf",
            "TestInterfaces": "pytest_nuts.base_tests.napalm_interfaces"
        }

        self.index = index if index is not None else default_index

    def find_test_module_of_class(self, name: str) -> Optional[str]:
        """
        Try to resolve the name of the test class to a module.

        :param name: The name of the test class.
        :return: The path of the module which contains the test class.
        """
        return self.index.get(name)
