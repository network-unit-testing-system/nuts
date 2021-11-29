"""Provide necessary information that is needed for a specific test."""
import pathlib
from typing import Any, Callable, Optional, Dict
from _pytest.config import Config

from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.task import AggregatedResult, Result
from nornir.core.filter import F

from nuts.helpers.errors import NutsSetupError
from nuts.helpers.result import AbstractResultExtractor
from nuts.helpers.filters import filter_hosts


class NutsContext:
    """
    Base context class. Holds all necessary information that is needed
    for a specific test.

    :param nuts_parameters: test-specific data that is defined in the test bundle,
        i.e. the yaml file that is converted to nuts tests
    """

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

    def __init__(
        self, nuts_parameters: Any = None, pytestconfig: Optional[Config] = None
    ):
        super().__init__(nuts_parameters, pytestconfig)
        self.nornir: Optional[Nornir] = None

    def initialize(self) -> None:
        if self.pytestconfig:
            config_file = pathlib.Path(
                self.pytestconfig.getoption("nornir_configuration")
            )
        else:
            config_file = pathlib.Path(self.DEFAULT_NORNIR_CONFIG_FILE)

        self.nornir = InitNornir(
            config_file=str(config_file),
            logging={"enabled": False},
        )

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
        return filter_hosts(self.nuts_parameters["test_data"])

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
