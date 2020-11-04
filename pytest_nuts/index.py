class TestIndex:
    def __init__(self, index=None):
        default_index = {
            'TestNetmikoCdpNeighbors': 'pytest_nuts.base_tests.netmiko_cdp_neighbors',
            'TestNetmikoPing': 'pytest_nuts.base_tests.netmiko_ping',
        }

        self.index = index if index is not None else default_index

    def find_test_module_of_class(self, name: str) -> str:
        return self.index.get(name)
