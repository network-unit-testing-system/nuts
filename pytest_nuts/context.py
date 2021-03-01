from typing import Any, Callable

from nornir.core.task import AggregatedResult

from pytest_nuts.helpers.errors import NutsSetupError


class NutsContext:
    """
    Base context class. Holds all necessary information that is needed for a specific test.

    :param nuts_parameters: test-specific data that is defined in the test bundle (e.g. the yaml file that is parsed by yaml_to_test)
    """

    def __init__(self, nuts_parameters: Any):
        self.nuts_parameters = nuts_parameters


class NornirNutsContext(NutsContext):
    """
    NutsContext class which provides nornir-specific helpers.
    It is meant to be inherited and implemented fully by test classes which use nornir.

    :param _transformed_result: All parsed results from a nornir task
    :param nornir: The initialized nornir instance

    """

    def __init__(self, nuts_parameters: Any):
        super().__init__(nuts_parameters)
        self._transformed_result = None
        self.nornir = None

    def nuts_task(self) -> Callable:
        """
        Returns the task that nornir should execute for the test module.

        :return: A task as defined by one of nornir's plugins or a function that calls a nornir task
        """
        raise NotImplementedError

    def nuts_arguments(self) -> dict:
        """
        Additional arguments for the nornir task to be executed. These can also be parameters
        that are defined in the `test_execution` part of the test bundle.
        Note that the arguments provided here must match those that the nornir task offers.

        :return: A dict containing the additional arguments
        """
        return {}

    def nornir_filter(self):
        """
        :return: A nornir filter that is applied to the nornir instance
        """
        return None

    def transform_result(self, general_result: AggregatedResult) -> Any:
        """
        Transforms the raw nornir result and wraps it into a `NutsResult`.

        :param general_result: The raw answer as provided by nornir's executed task
        :return: Usually a dict where keys are the hosts, values are a `NutsResult`
        """
        return general_result

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
        nuts_task = self.nuts_task()
        nuts_arguments = self.nuts_arguments()
        nornir_filter = self.nornir_filter()
        initialized_nornir = self.nornir

        if nornir_filter:
            selected_hosts = initialized_nornir.filter(nornir_filter)
        else:
            selected_hosts = initialized_nornir
        overall_results = selected_hosts.run(task=nuts_task, **nuts_arguments)

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

    @property
    def transformed_result(self) -> Any:
        """
        The result from nornir's task, transformed to be passed on later to a test's fixture
        called `single_result`.
        :return: The transformed result
        """
        if not self._transformed_result:
            self._transformed_result = self.transform_result(self.general_result())
        return self._transformed_result