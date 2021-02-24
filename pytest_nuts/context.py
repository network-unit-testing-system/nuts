from typing import Any, Callable

from nornir.core.task import AggregatedResult

from pytest_nuts.helpers.errors import NutsSetupError


class NutsContext:
    """
    Base context class that holds all necessary information that is needed for a specific test.

    :param nuts_parameters: test-specific data that is defined in the test bundle, i.e. the yaml file that is parsed by yaml_to_test.
    """

    def __init__(self, nuts_parameters: Any):
        self.nuts_parameters = nuts_parameters


class NornirNutsContext(NutsContext):
    """
    NutsContext class which provides nornir-specific helpers.

    :param _transformed_result
    :param nornir holds the initialized nornir instance.

    """

    def __init__(self, nuts_parameters: Any):
        super().__init__(nuts_parameters)
        self._transformed_result = None
        self.nornir = None

    def nuts_task(self) -> Callable:
        """
        Returns the task that nornir should execute for the test class.

        :return: A task as defined by one of nornir's plugins or a function that calls one.
        """
        raise NotImplementedError

    def nuts_arguments(self) -> dict:
        """
        Additional arguments for the nornir task that is executed. These can also be parameters
        that are defined in the `test_execution` part of the test bundle.
        Note that the arguments provided here must match those that the nornir task offers.

        :return: A dict containing the additional arguments.
        """
        return {}

    def nornir_filter(self):
        """
        :return: A nornir filter that is applied to the tornir instance.
        """
        return None

    def transform_result(self, general_result: Callable) -> Any:
        """
        Transforms the raw nornir result and wraps it into a `NutsResult`.
        :param general_result: The raw answer as provided by nornir's executed task.
        :return:
        """
        return general_result

    def general_result(self) -> AggregatedResult:
        """
        Nornir is run with the defined task, additional arguments, a nornir filter and returns the
        raw answer from nornir.
        If the setup/teardown methods are overwritten, these are executed as well.
        :return: The raw answer as provided by nornir's executed task.
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
        Defines setup code which is executed before the nornir task is executed.
        """
        pass

    def teardown(self):
        """
        Defines setup code which is executed after the nornir task is executed.
        """
        pass

    @property
    def transformed_result(self):
        if not self._transformed_result:
            self._transformed_result = self.transform_result(self.general_result())
        return self._transformed_result
