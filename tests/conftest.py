import pytest

from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.plugins.runners import RunnersPluginRegister

from tests.utils import YAML_EXTENSION


pytest_plugins = ["pytester", "nuts"]


@pytest.fixture
def deregister_nornir_plugin():
    # Cleanup Nornir's PluginRegisters.
    # This is necessary as InitNornir is initiated for every test case, but the
    # PluginRegisters are (somehow) shared. This results in a
    # PluginAlreadyRegistered Exception as the plugins are registered multiple
    # times.
    yield
    ConnectionPluginRegister.deregister_all()
    InventoryPluginRegister.deregister_all()
    RunnersPluginRegister.deregister_all()


@pytest.fixture
def default_nr_init(pytester, deregister_nornir_plugin):
    """Create initial Nornir files and expose the location
    as nornir_config_file fixture."""
    hosts_path = pytester.path / f"hosts{YAML_EXTENSION}"
    groups_path = pytester.path / f"groups{YAML_EXTENSION}"
    config = f"""inventory:
                    plugin: SimpleInventory
                    options:
                        host_file: {hosts_path}
                        group_file: {groups_path}
              """
    arguments = {
        "nr-config": config,
        "hosts": """
            R1:
              hostname: 1.1.1.1
              groups:
                - routers
                - site1
              data:
                tags:
                  - tag1
                  - router
            R2:
              hostname: 2.2.2.2
              groups:
                - routers
              data:
                tags:
                  - tag2
                  - router
            R3:
              hostname: 3.3.3.3
              groups:
                - routers
            L1:
              hostname: 11.11.11.11
            L2:
              hostname: 22.22.22.22
            S1:
              hostname: 111.111.111.111
            S2:
              hostname: 222.222.222.222
            """,
        "groups": """
            routers: {}
            site1: {}
            """,
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    # We need to have the test tmpdir in sys.path, so NUTS can import the test
    # modules (e.g. basic_task.py).
    pytester.syspathinsert()

    yield
