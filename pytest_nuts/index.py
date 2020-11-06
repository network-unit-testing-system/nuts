from typing import Dict


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
            'TestNetmikoCdpNeighbors': 'pytest_nuts.base_tests.netmiko_cdp_neighbors',
            'TestNetmikoPing': 'pytest_nuts.base_tests.netmiko_ping',
        }

        self.index = index if index is not None else default_index

    def find_test_module_of_class(self, name: str) -> str:
        """
        Try to resolve the name of the test class to a module.

        :param name: The name of the test class
        :return: The path of the module which contains the test class
        """
        return self.index.get(name)
