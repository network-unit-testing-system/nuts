from typing import Any, Callable

from nornir.core.task import AggregatedResult

from pytest_nuts.helpers.errors import NutsSetupError


class NutsContext:
    """
    Base context class that holds all necessary information that is needed for a specific test.
    nuts_parameters: test-specific data that can be retrieved via yaml_to_test from a YAML file.
    """

    def __init__(self, nuts_parameters: Any):
        self.nuts_parameters = nuts_parameters


class NornirNutsContext(NutsContext):
    """
    NutsContext class which provides nornir-specific helpers.
    """

    def __init__(self, nuts_parameters: Any):
        super().__init__(nuts_parameters)
        self._transformed_result = None
        self.nornir = None

    def nuts_task(self) -> Callable:
        raise NotImplementedError

    def nuts_arguments(self) -> dict:
        if self.nuts_parameters["test_execution"]:
            return {**self.nuts_parameters["test_execution"]}
        return {}


    def nornir_filter(self):
        return None

    def transform_result(self, general_result: AggregatedResult) -> Any:
        return general_result

    def general_result(self) -> AggregatedResult:
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
        pass

    def teardown(self):
        pass

    @property
    def transformed_result(self) -> Any:
        if not self._transformed_result:
            self._transformed_result = self.transform_result(self.general_result())
        return self._transformed_result
