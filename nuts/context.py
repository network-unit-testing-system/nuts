"""Provide necessary information that is needed for a specific test."""
import pathlib
from typing import Any, Callable, Optional, Dict, Union

from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.task import AggregatedResult

from nuts.helpers.errors import NutsSetupError
from nuts.helpers.result import NutsResult


_TransformedResult = Dict[str, Any]


class NutsContext:
    """
    Base context class. Holds all necessary information that is needed for a specific test.

    :param nuts_parameters: test-specific data that is defined in the test bundle, i.e. the yaml file that is converted to nuts tests
    """

    def __init__(self, nuts_parameters: Any = None):
        self.nuts_parameters = nuts_parameters or {}
        self._cached_result: Optional[_TransformedResult] = None

    def initialize(self) -> None:
        """Initialize dependencies for this context after it has been created."""
        pass

    def nuts_arguments(self) -> dict:
        """
        Additional arguments for the (network) task to be executed. These can also be parameters
        that are defined in the `test_execution` part of the test bundle.

        If the subclass is a NornirNutsContext, the arguments are passed on to the nornir task:
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

    def transform_result(self, general_result: Any) -> _TransformedResult:
        """
        :param general_result: raw result
        :return: processed result ready to be passed to a test
        """
        raise NotImplementedError

    @property
    def transformed_result(self) -> _TransformedResult:
        """
        The (processed) results of the network task, ready to be passed on to a test's fixture.
        The results are cached, so that general_result does not need to be called multiple times as it might
        access the network.
        """
        if self._cached_result is None:
            self._cached_result = self.transform_result(self.general_result())
        return self._cached_result


class NornirNutsContext(NutsContext):
    """
    NutsContext class which provides nornir-specific helpers.
    It is meant to be inherited and implemented fully by test classes which use nornir.

    :param _transformed_result: All parsed results from a nornir task
    :param nornir: The initialized nornir instance

    """

    #: The path to a nornir configuration file.
    #: https://nornir.readthedocs.io/en/stable/configuration/index.html
    NORNIR_CONFIG_FILE = pathlib.Path("nr-config.yaml")

    def __init__(self, nuts_parameters: Any = None):
        super().__init__(nuts_parameters)
        self.nornir: Optional[Nornir] = None

    def initialize(self) -> None:
        self.nornir = InitNornir(
            config_file=str(self.NORNIR_CONFIG_FILE),
            logging={"enabled": False},
        )

    def nuts_task(self) -> Callable:
        """
        Returns the task that nornir should execute for the test module.

        :return: A task as defined by one of nornir's plugins or a function that calls a nornir task
        """
        raise NotImplementedError

    def nornir_filter(self):
        """
        :return: A nornir filter that is applied to the nornir instance
        """
        return None

    def transform_result(self, general_result: AggregatedResult) -> Dict[str, Any]:
        """
        Transforms the raw nornir result and wraps it into a `NutsResult`.

        :param general_result: The raw answer as provided by nornir's executed task
        :return: A dict where keys are the hosts, values are a `NutsResult`
        """
        raise NotImplementedError

    def general_result(self) -> AggregatedResult:
        """
        Nornir is run with the defined task, additional arguments, a nornir filter and returns the
        raw result from nornir.
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
        overall_results = selected_hosts.run(task=self.nuts_task(), **self.nuts_arguments())

        self.teardown()
        return overall_results

    def setup(self):
        """
        Defines code which is executed before the nornir task.
        """
        pass

    def teardown(self):
        """
        Defines code which is executed after the nornir task.
        """
        pass
