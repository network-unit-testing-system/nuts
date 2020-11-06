from typing import Dict


class ModuleIndex:
    """
    Helps to simplify test definitions by registering the module of a test class.
    Thus in the test definitions the module is no longer needed.
    """

    def __init__(self, index: Dict[str, str] = None):
        """
        Creates a new ModuleIndex

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
