from typing import Any, Dict, List
from unittest.mock import Mock, ANY

import pytest

from nuts.context import NornirNutsContext, NutsSetupError, NutsContext
from tests.utils import YAML_EXTENSION


class CustomNornirNutsContext(NornirNutsContext):
    def __init__(self, nuts_parameters, pytestconfig):
        super().__init__(nuts_parameters, pytestconfig)
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
    inventory_data = {
        "R1": {"name": "R1", "tags": ["router", "tag1"], "groups": ["router", "site1"]},
        "R2": {"name": "R2", "tags": ["router", "tag2"], "groups": ["router", "site2"]},
    }

    def nornir_mock(f=None):
        if f:
            data: Dict[str, Dict[str, Any]] = {}
            for host in inventory_data.values():
                if f(host):
                    data[str(host["name"])] = host
        else:
            data = inventory_data

        m = Mock()
        m.inventory.hosts.keys.return_value = data.keys()
        return m

    mock = nornir_mock()

    # No nested filters supported
    mock.filter.side_effect = nornir_mock
    return mock


@pytest.fixture
def nornir_nuts_ctx(nornir_instance):
    context = CustomNornirNutsContext({}, None)
    context.nornir = nornir_instance
    return context


class TestNornirNutsContextTestExecutionField:
    def test_test_execution_not_existing(self):
        context = NutsContext({})
        assert context.nuts_arguments() == {}

    def test_test_execution_exists_but_empty(self):
        context = NutsContext({"test_execution": None})
        assert context.nuts_arguments() == {}

    def test_test_execution_contains_data(self):
        context = NutsContext({"test_execution": {"count": 42, "ref": 23}})
        assert context.nuts_arguments() == {"count": 42, "ref": 23}


class TestNornirNutsContextGeneralResult:
    def test_raises_nuts_setup_error_if_nornir_is_not_defined(self):
        with pytest.raises(NutsSetupError):
            ctx = CustomNornirNutsContext({}, None)

            ctx.general_result()

    def test_filters_inventory_based_on_nornir_filter(
        self, nornir_nuts_ctx, nornir_instance
    ):
        nornir_nuts_ctx.test_filter = Mock()

        nornir_nuts_ctx.general_result()

        nornir_instance.filter.assert_called_with(nornir_nuts_ctx.test_filter)

    def test_calls_run_on_filtered_inventory(self, nornir_nuts_ctx, nornir_instance):
        filtered_inventory = Mock()
        nornir_instance.filter = Mock()
        nornir_instance.filter.return_value = filtered_inventory
        nornir_nuts_ctx.test_filter = Mock()

        nornir_nuts_ctx.general_result()

        assert filtered_inventory.run.called

    def test_passes_nuts_arguments_to_nornir(self, nornir_nuts_ctx, nornir_instance):
        nornir_nuts_ctx.test_arguments = {"test": "test123", "test2": "test456"}

        nornir_nuts_ctx.general_result()

        nornir_instance.run.assert_called_with(
            task=ANY, test="test123", test2="test456"
        )

    def test_runs_nuts_task_on_inventory(self, nornir_nuts_ctx, nornir_instance):
        nornir_nuts_ctx.general_result()

        nornir_instance.run.assert_called_with(task=nornir_nuts_ctx.nuts_task())

    def test_returns_nornir_result(self, nornir_nuts_ctx, nornir_instance):
        nornir_results = Mock()
        nornir_instance.run.return_value = nornir_results

        result = nornir_nuts_ctx.general_result()

        assert result == nornir_results


@pytest.mark.usefixtures("default_nr_init")
class TestNornirNutsContextIntegration:
    def test_fails_if_no_task_is_defined(self, pytester):
        pytester.makepyfile(
            basic_task="""
            from nuts.context import NornirNutsContext


            class FailingNornirNutsContext(NornirNutsContext):
                pass

            CONTEXT = FailingNornirNutsContext

            class TestBasicTask:
                def test_basic_task(self, nuts_ctx):
                    assert nuts_ctx.general_result()["R1"].result == "R1"
            """
        )
        arguments = {
            "test_class_loading": """
                        ---
                        - test_module: basic_task
                          test_class: TestBasicTask
                          test_data:
                            - host: R1
                            - host: R2
                        """,
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(failed=1)

    def test_executes_specified_task(self, pytester):
        pytester.makepyfile(
            basic_task="""
    from nuts.context import NornirNutsContext


    class CustomNornirNutsContext(NornirNutsContext):
        def nuts_task(self):
            return lambda task: task.host.name


    CONTEXT = CustomNornirNutsContext


    class TestBasicTask:
        def test_basic_task(self, nuts_ctx):
            assert nuts_ctx.general_result()["R1"].result == "R1"
    """
        )
        arguments = {
            "test_class_loading": """
                ---
                - test_module: basic_task
                  test_class: TestBasicTask
                  test_data:
                    - host: R1
                    - host: R2
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(passed=1)

    def test_wrong_host_in_test(self, pytester):
        pytester.makepyfile(
            basic_task="""
        from nuts.context import NornirNutsContext
        from nuts.helpers.errors import NutsSetupError
        from nornir.core.filter import F
        from nuts.helpers.filters import filter_hosts

        import pytest


        class CustomNornirNutsContext(NornirNutsContext):

            def nuts_task(self):
                return lambda task: task.host.name


        CONTEXT = CustomNornirNutsContext


        class TestBasicTask:
            @pytest.mark.xfail(raises=NutsSetupError)
            def test_basic_task(self, nuts_ctx):
                pass
        """
        )
        arguments = {
            "test_class_loading": """
                    ---
                    - test_module: basic_task
                      test_class: TestBasicTask
                      test_data:
                        - host: S1
                        - host: S2
                    """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(xpassed=1)


@pytest.mark.usefixtures("default_nr_init")
class TestNornirNutsContextCaching:
    BASIC_TASK = """
    import pytest
    from nornir.core.task import Result
    from nuts.context import NornirNutsContext
    from nuts.helpers.result import AbstractHostResultExtractor


    class ExpanseExtractor(AbstractHostResultExtractor):
        def single_transform(self, single_result):
            return self._simple_extract(single_result)

    class CustomNornirNutsContext(NornirNutsContext):
        def nuts_task(self):
            return lambda task: Result(host=task.host, result=task.host.name)

        def nuts_extractor(self) -> ExpanseExtractor:
            return ExpanseExtractor(self)

        def teardown(self) -> None:
            # Manipulate the cashe, will be executed by
            if self.pytestconfig and self.pytestconfig.cache:
                if nc := self.pytestconfig.cache.get("nuts/NORNIR_CACHE", None):
                    nc["hosts"]["R1"]["data"]["new"] = "manipulate cashe"
                    self.pytestconfig.cache.set("nuts/NORNIR_CACHE", nc)

    CONTEXT = CustomNornirNutsContext

    class TestBasicTaskFirst:
        def test_config_has_cache(self, nuts_ctx):
            nornir_cache = nuts_ctx.pytestconfig.cache.get("nuts/NORNIR_CACHE", {})
            assert "hosts" in nornir_cache
            assert "groups" in nornir_cache
            assert "defaults" in nornir_cache
            assert "R1" in nornir_cache["hosts"]

            assert "new" not in nornir_cache["hosts"]["R1"]["data"]

        def test_has_correct_pytestconfig(self, nuts_ctx):
            assert not nuts_ctx.pytestconfig.getoption("nornir_cache_disabled")

        @pytest.mark.nuts("host")
        def test_trigger_teardown(self, nuts_ctx, single_result, host):
            assert host == "R1"


    class TestBasicTaskSecond:
        def test_config_has_cache(self, nuts_ctx):
            nornir_cache = nuts_ctx.pytestconfig.cache.get("nuts/NORNIR_CACHE", {})
            assert "hosts" in nornir_cache
            assert "groups" in nornir_cache
            assert "defaults" in nornir_cache
            assert "R1" in nornir_cache["hosts"]

            print(nornir_cache["hosts"]["R1"]["data"])

            assert "new" in nornir_cache["hosts"]["R1"]["data"]
            assert nornir_cache["hosts"]["R1"]["data"]["new"] == "manipulate cashe"
                """
    ARGUMENTS = {
        "test_class_loading": """
                        ---
                        - test_module: basic_task
                          test_class: TestBasicTaskFirst
                          test_data:
                            - host: R1
                        - test_module: basic_task
                          test_class: TestBasicTaskSecond
                          test_data:
                            - host: R1
                        """,
    }

    def test_cached_nornir_inventory(self, pytester, deregister_nornir_plugin):
        pytester.makepyfile(basic_task=self.BASIC_TASK)
        arguments = self.ARGUMENTS
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(passed=4)

        result = pytester.runpytest(
            "--nornir-cached-inventory", "--cache-show", "nuts/NORNIR_CACHE"
        )
        result.assert_outcomes()
        assert "hosts" in result.stdout.str()

    def test_no_cached_nornir_inventory(self, pytester, deregister_nornir_plugin):
        pytester.makepyfile(basic_task=self.BASIC_TASK)
        arguments = self.ARGUMENTS
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("--nornir-cache-disable", "-v")

        result.assert_outcomes(passed=1, failed=3)
        output = result.stdout.str()
        assert "test_config_has_cache FAILED" in output
        assert "test_has_correct_pytestconfig FAILED" in output
        assert "test_trigger_teardown[R1_] PASSED" in output
        assert "test_config_has_cache FAILED" in output


class TestNornirNutsContextIntegrationWithoutFiles:
    def test_nornir_config_cmdline_option(self, pytester, deregister_nornir_plugin):
        """
        Test the command line option to provide another nornir config file
        than the default one ("nr-config.yaml"). Basically tests whether it
        really loads the changed configuration, which overwrites the default
        test configuration.
        """
        # Setup other-config files
        hosts_path = pytester.path / f"other_hosts{YAML_EXTENSION}"
        config = f"""inventory:
                              plugin: SimpleInventory
                              options:
                                  host_file: {hosts_path}
        """
        arguments = {
            "other-nr-config": config,
            "other_hosts": """
                R1:
                  hostname: 10.10.10.10
                R2:
                  hostname: 20.20.20.20
                R3:
                  hostname: 30.30.30.30
                R4:
                  hostname: 40.40.40.40
                L1:
                  hostname: 111.111.111.111
            """,
        }

        pytester.makefile(YAML_EXTENSION, **arguments)

        # Now make the real test
        pytester.makepyfile(
            basic_task="""
    from nuts.context import NornirNutsContext


    class CustomNornirNutsContext(NornirNutsContext):
        pass


    CONTEXT = CustomNornirNutsContext


    class TestOtherConfigFile:
        def test_has_correct_pytestconfig(self, nuts_ctx):
            assert nuts_ctx.pytestconfig.getoption("nornir_configuration") == "other-nr-config.yaml"  # noqa: E501

        def test_overrides_r1(self, nuts_ctx):
            assert nuts_ctx.nornir.inventory.hosts["R1"].hostname == "10.10.10.10"

        def test_has_added_r4(self, nuts_ctx):
            assert nuts_ctx.nornir.inventory.hosts["R4"].hostname == "40.40.40.40"

        def test_has_removed_l2(self, nuts_ctx):
            assert "L2" not in nuts_ctx.nornir.inventory.hosts.keys()
    """
        )
        pytester.syspathinsert()
        arguments = {
            "test_class_loading": """
                ---
                - test_module: basic_task
                  test_class: TestOtherConfigFile
                  test_data:
                    - host: R1
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest(
            "test_class_loading.yaml", "--nornir-config", "other-nr-config.yaml"
        )
        result.assert_outcomes(passed=4)


class TestContextParameterization:
    def test_default_parametrization(self):
        context = NutsContext()
        test_data = {"host": "R1", "test": "test"}
        assert context.parametrize(test_data) == test_data

    def test_custom_parametrization(self):
        class CustomContext(NutsContext):
            def parametrize(
                self, test_data: List[Dict[str, Any]]
            ) -> List[Dict[str, Any]]:
                return [
                    data for data in test_data for _ in range(data.get("multiplier", 1))
                ]

        context = CustomContext()
        test_data = [{"multiplier": 4, "test": "test"}]
        new_test_data = context.parametrize(test_data)
        assert len(new_test_data) == 4


class TestNornirContextParametrization:
    def test_raises_nuts_setup_error_if_nornir_is_not_defined(self):
        with pytest.raises(NutsSetupError):
            context = NornirNutsContext()
            test_data = [{"host": "R1", "test": "test"}]
            context.parametrize(test_data) == test_data

    @pytest.mark.parametrize(
        "test_data, expected",
        [
            # host tests
            ([{"host": "R1", "test": "test"}], [{"host": "R1", "test": "test"}]),
            ([{"host": "R2", "test": "test"}], [{"host": "R2", "test": "test"}]),
            (
                [{"host": ["R1", "R2"], "test": "test"}],
                [{"host": "R1", "test": "test"}, {"host": "R2", "test": "test"}],
            ),
            (
                [{"host": "R1", "tags": [], "groups": [], "test": "test"}],
                [{"host": "R1", "test": "test"}],
            ),
            # tags tests
            (
                [{"tags": ["tag1"], "test": "test"}],
                [{"host": "R1", "test": "test"}],
            ),
            (
                [{"tags": ["tag2"], "test": "test"}],
                [{"host": "R2", "test": "test"}],
            ),
            (
                [{"tags": ["router"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                    {"host": "R2", "test": "test"},
                ],
            ),
            (
                [{"host": "R1", "tags": ["router"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                    {"host": "R2", "test": "test"},
                ],
            ),
            (
                [{"host": "R1", "tags": ["tag2"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                    {"host": "R2", "test": "test"},
                ],
            ),
            (
                [{"host": "R1", "tags": ["tag1"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                ],
            ),
            (
                [{"host": "R1", "tags": ["notFound"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                ],
            ),
            # groups tests
            (
                [{"groups": ["site1"], "test": "test"}],
                [{"host": "R1", "test": "test"}],
            ),
            (
                [{"groups": ["site2"], "test": "test"}],
                [{"host": "R2", "test": "test"}],
            ),
            (
                [{"groups": ["router"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                    {"host": "R2", "test": "test"},
                ],
            ),
            (
                [{"host": "R2", "groups": ["router"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                    {"host": "R2", "test": "test"},
                ],
            ),
            (
                [{"host": "R2", "groups": ["site1"], "test": "test"}],
                [
                    {"host": "R1", "test": "test"},
                    {"host": "R2", "test": "test"},
                ],
            ),
            (
                [{"host": "R2", "groups": ["site2"], "test": "test"}],
                [
                    {"host": "R2", "test": "test"},
                ],
            ),
            (
                [{"host": "R2", "groups": ["notFound"], "test": "test"}],
                [
                    {"host": "R2", "test": "test"},
                ],
            ),
        ],
    )
    def test_parametrization_single_host(self, nornir_nuts_ctx, test_data, expected):
        new_data = nornir_nuts_ctx.parametrize(test_data)
        assert len(new_data) == len(expected)
        for d in expected:
            assert d in new_data


@pytest.mark.usefixtures("default_nr_init")
class TestNornirNutsContextParametrizationIntegration:
    BASIC_TASK = """
    import pytest
    from nornir.core.task import Result
    from nuts.context import NornirNutsContext
    from nuts.helpers.result import AbstractHostResultExtractor

    class ExpanseExtractor(AbstractHostResultExtractor):
        def single_transform(self, single_result):
            return self._simple_extract(single_result)

    class CustomNornirNutsContext(NornirNutsContext):
        def nuts_task(self):
            return lambda task: Result(host=task.host, result=task.host.name)

        def nuts_extractor(self) -> ExpanseExtractor:
            return ExpanseExtractor(self)


    CONTEXT = CustomNornirNutsContext


    class TestBasicTask:
        @pytest.mark.nuts("host")
        def test_basic_task(self, single_result, host):
            assert single_result.result == host
    """

    def test_executes_task_with_tags(self, pytester):
        pytester.makepyfile(basic_task=self.BASIC_TASK)
        arguments = {
            "test_class_loading": """
                ---
                - test_module: basic_task
                  test_class: TestBasicTask
                  test_data:
                    - tags: tag1
                    - tags: tag2
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(passed=2)

    def test_executes_task_with_tag_routers(self, pytester):
        pytester.makepyfile(basic_task=self.BASIC_TASK)
        arguments = {
            "test_class_loading": """
                ---
                - test_module: basic_task
                  test_class: TestBasicTask
                  test_data:
                    - tags: router
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(passed=2)

    def test_executes_task_with_group_site1(self, pytester):
        pytester.makepyfile(basic_task=self.BASIC_TASK)
        arguments = {
            "test_class_loading": """
                ---
                - test_module: basic_task
                  test_class: TestBasicTask
                  test_data:
                    - groups: site1
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(passed=1)

    def test_executes_task_with_group_routers(self, pytester):
        pytester.makepyfile(basic_task=self.BASIC_TASK)
        arguments = {
            "test_class_loading": """
                ---
                - test_module: basic_task
                  test_class: TestBasicTask
                  test_data:
                    - groups: routers
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(passed=3)

    def test_executes_task_fail_no_host_found(self, pytester):
        pytester.makepyfile(basic_task=self.BASIC_TASK)
        arguments = {
            "test_class_loading": """
                ---
                - test_module: basic_task
                  test_class: TestBasicTask
                  test_data:
                    - groups: notExisting
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        result.assert_outcomes(errors=1)

    def test_executes_napalm_interface_count_tests(self, pytester):
        arguments = {
            "test_class_loading": """
                ---
                - test_class: TestNapalmInterfaces
                  test_data:
                    - tags:
                        - router
                      name: eth-0/1
                      is_enabled: true
                      is_up: true
                      # mac_address: <MAC address>
                      # mtu: <int value>
                      # speed: <int value>
                """
        }
        pytester.makefile(YAML_EXTENSION, **arguments)
        result = pytester.runpytest("test_class_loading.yaml")
        # Router R1 and R2 have the tag "router"
        # 3*2 tests should be skipped
        # 2*2 tests should faile with an error (No napalm driver provided)
        result.assert_outcomes(skipped=6, errors=4)
