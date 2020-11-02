module_index = {
    'TestNetmikoCdpNeighbors': 'pytest_nuts.base_tests.netmiko_cdp_neighbors',
    'TestNetmikoPing': 'pytest_nuts.base_tests.netmiko_ping',
}


def find_test_module_of_class(name: str) -> str:
    return module_index.get(name)
