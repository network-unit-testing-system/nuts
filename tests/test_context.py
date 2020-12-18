from unittest.mock import Mock, ANY

import pytest

from pytest_nuts.context import NornirNutsContext, NutsSetupError


class CustomNornirNutsContext(NornirNutsContext):
    def __init__(self, nuts_parameters):
        super().__init__(nuts_parameters)
        self.test_filter = None
        self.test_task = lambda task: task.host.name
        self.test_arguments = {}

    def nuts_arguments(self):
        return self.test_arguments

    def nuts_task(self):
        return self.test_task

    def nornir_filter(self):
        return self.test_filter


@pytest.fixture
def nornir_instance():
    return Mock()


@pytest.fixture
def nornir_nuts_ctx(nornir_instance):
    context = CustomNornirNutsContext({})
    context.nornir = nornir_instance
    return context


class TestNornirNutsContextGeneralResult:
    def test_raises_nuts_setup_error_if_nornir_is_not_defined(self):
        with pytest.raises(NutsSetupError):
            ctx = CustomNornirNutsContext({})

            ctx.general_result()

    def test_filters_inventory_based_on_nornir_filter(self, nornir_nuts_ctx, nornir_instance):
        nornir_nuts_ctx.test_filter = Mock()

        nornir_nuts_ctx.general_result()

        nornir_instance.filter.assert_called_with(nornir_nuts_ctx.test_filter)

    def test_calls_run_on_filtered_inventory(self, nornir_nuts_ctx, nornir_instance):
        filtered_inventory = Mock()
        nornir_instance.filter.return_value = filtered_inventory
        nornir_nuts_ctx.test_filter = Mock()

        nornir_nuts_ctx.general_result()

        assert filtered_inventory.run.called

    def test_passes_nuts_arguments_to_nornir(self, nornir_nuts_ctx, nornir_instance):
        nornir_nuts_ctx.test_arguments = {'test': 'test123', 'test2': 'test456'}

        nornir_nuts_ctx.general_result()

        nornir_instance.run.assert_called_with(task=ANY, test='test123', test2='test456')

    def test_runs_nuts_task_on_inventory(self, nornir_nuts_ctx, nornir_instance):
        nornir_nuts_ctx.general_result()

        nornir_instance.run.assert_called_with(task=nornir_nuts_ctx.nuts_task())

    def test_returns_nornir_result(self, nornir_nuts_ctx, nornir_instance):
        nornir_results = Mock()
        nornir_instance.run.return_value = nornir_results

        result = nornir_nuts_ctx.general_result()

        assert result == nornir_results


class TestNornirNutsContextTransformedResult:
    pass
