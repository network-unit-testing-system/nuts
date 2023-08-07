import pytest

from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.plugins.runners import RunnersPluginRegister

from tests.utils import YAML_EXTENSION


pytest_plugins = ["pytester", "nuts"]


@pytest.fixture
def default_nr_init(pytester):
    """Create initial Nornir files and expose the location
    as nornir_config_file fixture."""
    hosts_path = pytester.path / f"hosts{YAML_EXTENSION}"
    config = f"""inventory:
                          plugin: SimpleInventory
                          options:
                              host_file: {hosts_path}"""
    arguments = {
        "nr-config": config,
        "hosts": """
            R1:
              hostname: 1.1.1.1
              data:
                tags:
                  - tag1
                  - router
            R2:
              hostname: 2.2.2.2
              data:
                tags:
                  - tag2
                  - router
            R3:
              hostname: 3.3.3.3
            L1:
              hostname: 11.11.11.11
            L2:
              hostname: 22.22.22.22
            S1:
              hostname: 111.111.111.111
            S2:
              hostname: 222.222.222.222""",
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    # We need to have the test tmpdir in sys.path, so NUTS can import the test
    # modules (e.g. basic_task.py).
    pytester.syspathinsert()

    yield

    # Cleanup Nornir's PluginRegisters.
    # This is necessary as InitNornir is initiated for every test case, but the
    # PluginRegisters are (somehow) shared. This results in a
    # PluginAlreadyRegistered Exception as the plugins are registered multiple
    # times.
    ConnectionPluginRegister.deregister_all()
    InventoryPluginRegister.deregister_all()
    RunnersPluginRegister.deregister_all()
