"""Provide necessary information that is needed for a specific test."""

import pathlib
from typing import Any, Callable, Optional, Dict, List
from pytest import Config

from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.task import AggregatedResult, Result
from nornir.core.filter import F
from nornir.core.plugins.inventory import InventoryPluginRegister

from nuts.helpers.errors import NutsSetupError
from nuts.helpers.result import AbstractResultExtractor
from nuts.helpers.filters import filter_hosts, get_filter_object
from nuts.helpers.cache import serialize_inventory, CacheInventory


class NutsContext:
    """
    Base context class. Holds all necessary information that is needed
    for a specific test.

    :param nuts_parameters: test-specific data that is defined in the test bundle,
        i.e. the yaml file that is converted to nuts tests
    """

    id_format: str = ""

    def __init__(
        self, nuts_parameters: Any = None, pytestconfig: Optional[Config] = None
    ):
        self.nuts_parameters = nuts_parameters or {}
        self.extractor = self.nuts_extractor()
        self._pytestconfig = pytestconfig

    def initialize(self) -> None:
        """Initialize dependencies for this context after it has been created."""
        pass

    def nuts_extractor(self) -> AbstractResultExtractor:
        """Get a result extractor for this context."""
        return AbstractResultExtractor(self)

    def nuts_arguments(self) -> Dict[str, Any]:
        """
        Additional arguments for the (network) task to be executed.
        These can also be parameters that are defined in the `test_execution`
        part of the test bundle.

        If the subclass is a NornirNutsContext, the arguments are passed on
        to the nornir task:
        Note that the arguments then must match those that the nornir task offers.

        :return: A dict containing the additional arguments
        """
        test_execution = self.nuts_parameters.get("test_execution", None)
        return {**(test_execution if test_execution is not None else {})}

    def general_result(self) -> Any:
        """
        :return: raw, unprocessed result
        """
        raise NotImplementedError

    @property
    def pytestconfig(self) -> Optional[Config]:
        """
        Set the pytest configuration.

        Can be overwritten to aggregate the configuration
        """
        return self._pytestconfig

    def parametrize(self, test_data: Any) -> Any:
        """
        Return granular test_data depending on the Context.
        If test_data includes a kind of group selct this function should unpack
        and return test data for every host or entity.

        :return: A dict containing the data vor every entity
        """
        return test_data


class NornirNutsContext(NutsContext):
    """
    NutsContext class which provides nornir-specific helpers.
    It is meant to be inherited and implemented fully by test classes which use nornir.

    :param _transformed_result: All parsed results from a nornir task
    :param nornir: The initialized nornir instance

    """

    #: The path to a nornir configuration file.
    #: https://nornir.readthedocs.io/en/stable/configuration/index.html
    DEFAULT_NORNIR_CONFIG_FILE = "nr-config.yaml"

    # `_` to sepperate hostname from pytest number used for test with same name
    id_format = "{host}_"

    def __init__(
        self, nuts_parameters: Any = None, pytestconfig: Optional[Config] = None
    ):
        super().__init__(nuts_parameters, pytestconfig)
        self.nornir: Optional[Nornir] = None

    def initialize(self) -> None:
        """
        Checks if inventory should be cached, then use global inventory otherwise
        regenerate it continuously.
        """
        if self.pytestconfig:
            config_file = pathlib.Path(
                self.pytestconfig.getoption("nornir_configuration")
            )
        else:
            config_file = pathlib.Path(self.DEFAULT_NORNIR_CONFIG_FILE)

        if self.pytestconfig and self.pytestconfig.cache:
            if nornir_inventory := self.pytestconfig.cache.get(
                "nuts/NORNIR_CACHE", None
            ):
                InventoryPluginRegister.register("NutsCacheInventory", CacheInventory)

                self.nornir = InitNornir(
                    config_file=str(config_file),
                    logging={"enabled": False},
                    inventory={
                        "plugin": "NutsCacheInventory",
                        "options": nornir_inventory,
                    },
                )
                return

        self.nornir = InitNornir(
            config_file=str(config_file),
            logging={"enabled": False},
        )
        if self.pytestconfig and not self.pytestconfig.getoption(
            "nornir_cache_disabled"
        ):
            # pytest cash needs json encodable values
            inventory = serialize_inventory(self.nornir.inventory)
            if self.pytestconfig and self.pytestconfig.cache:
                self.pytestconfig.cache.set("nuts/NORNIR_CACHE", inventory)

    def nuts_task(self) -> Callable[..., Result]:
        """
        Returns the task that nornir should execute for the test module.

        :return: A task as defined by one of nornir's plugins
            or a function that calls a nornir task
        """
        raise NotImplementedError

    def nornir_filter(self) -> F:
        """
        :return: A nornir filter that is applied to the nornir instance
        """
        data = self.parametrize(self.nuts_parameters["test_data"])
        return filter_hosts(data)

    def parametrize(self, test_data: Any) -> Any:
        """
        Parametrize test_data with hosts.
        This is needed because of the support of `tags` and `groups`.

        :param test_data: test_data from YAML file

        :return: Parametrized test_data
        """
        if not self.nornir:
            raise NutsSetupError("First Nornir has to be loaded. Call `initialize`.")
        tests = []
        for data in test_data:
            filter_object = get_filter_object(data)
            nr = self.nornir.filter(filter_object)

            # keep explicit hosts in test_data
            def get_explicit_hosts(data: Any) -> List[str]:
                host = data.get("host", [])
                if isinstance(host, list):
                    return host
                return [host]

            explicit_hosts = get_explicit_hosts(data)
            inventory_hosts = list(nr.inventory.hosts.keys())
            if not inventory_hosts:
                raise NutsSetupError(
                    f"No hosts found for filter {filter_object} in Nornir inventory."
                )
            for host in set(explicit_hosts + inventory_hosts):
                new_data = data.copy()
                new_data.pop("groups", None)
                new_data.pop("tags", None)
                tests.append({**new_data, "host": host})

        return tests

    def general_result(self) -> AggregatedResult:
        """
        Nornir is run with the defined task, additional arguments,
            a nornir filter and returns the raw result from nornir.
        If the setup/teardown methods are overwritten, these are executed as well.

        :return: The raw result as provided by nornir's executed task
        """
        if not self.nornir:
            raise NutsSetupError("Nornir instance not found in context object")
        self.setup()
        nornir_filter = self.nornir_filter()

        if nornir_filter:
            selected_hosts = self.nornir.filter(nornir_filter)

        else:
            selected_hosts = self.nornir

        if not selected_hosts.inventory.hosts:
            if nornir_filter:
                raise NutsSetupError(
                    f'Host(s) "{",".join(nornir_filter.filters["name__any"])}" '
                    f"not found in the inventory."
                )
            else:
                raise NutsSetupError("No Hosts found, is the nornir inventory empty?")

        overall_results = selected_hosts.run(
            task=self.nuts_task(), **self.nuts_arguments()
        )

        self.teardown()
        selected_hosts.close_connections(on_good=True, on_failed=True)
        return overall_results

    def setup(self) -> None:
        """
        Defines code which is executed before the nornir task.
        """
        pass

    def teardown(self) -> None:
        """
        Defines code which is executed after the nornir task.
        """
        pass
