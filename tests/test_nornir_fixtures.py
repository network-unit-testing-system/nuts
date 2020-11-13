import pytest
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.plugins.runners import RunnersPluginRegister

from tests.helpers.shared import YAML_EXTENSION


@pytest.fixture
def nr_wrapper():
    """
    Cleanup Nornir's PluginRegisters.

    This is necessary as InitNornir is initiated for every test case, but the PluginRegisters are (somehow) shared.
    This results in a PluginAlreadyRegistered Exception as the plugins are registered multiple times.
    """
    yield None
    ConnectionPluginRegister.deregister_all()
    InventoryPluginRegister.deregister_all()
    RunnersPluginRegister.deregister_all()


@pytest.fixture
def default_nr_init(testdir):
    """Create initial Nornir files and expose the location as nornir_config_file fixture."""
    hosts_path_as_string = str(testdir.tmpdir.join(f"hosts{YAML_EXTENSION}"))
    config = f"""inventory:
                          plugin: SimpleInventory
                          options:
                              host_file: {hosts_path_as_string}"""
    arguments = {
        "nr-config": config,
        "hosts": """
            R1:
              hostname: 10.20.0.31
            R2:
              hostname: 10.20.0.32""",
    }
    testdir.makefile(YAML_EXTENSION, **arguments)
    nr_path_as_string = str(testdir.tmpdir.join(f"nr-config{YAML_EXTENSION}")).replace("\\", r"\\")
    conf_test = f"""
          from nornir.core import Task
          import pytest

          @pytest.fixture(scope="session")
          def nornir_config_file():
              return "{nr_path_as_string}"
                  """
    testdir.makeconftest(conf_test)


@pytest.mark.usefixtures("default_nr_init", "nr_wrapper")
def test_inject_general_result_fixture(testdir):
    testdir.makepyfile(
        """
        import pytest
        
        @pytest.fixture(scope="class")
        def nuts_task():
              return lambda task: None
              
        def test_basic_task(general_result):
            assert general_result is not None
        """
    )

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.usefixtures("default_nr_init", "nr_wrapper")
def test_errors_if_no_task_is_defined(testdir):
    testdir.makepyfile(
        """
        def test_basic_task(general_result):
            assert general_result is not None
        """
    )

    result = testdir.runpytest()
    result.assert_outcomes(errors=1)


@pytest.mark.usefixtures("default_nr_init", "nr_wrapper")
def test_executes_specified_task(testdir):
    testdir.makepyfile(
        """
        import pytest
        
        @pytest.fixture(scope="class")
        def nuts_task():
            return lambda task: task.host.name
            
        def test_basic_task(general_result):
            assert general_result['R1'].result == 'R1'
        """
    )

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.usefixtures("default_nr_init", "nr_wrapper")
def test_filters_hosts(testdir):
    testdir.makepyfile(
        """
        import pytest
        from nornir.core.filter import F
        
        @pytest.fixture(scope="class")
        def nuts_task():
            return lambda task: None
            
        @pytest.fixture(scope="class")
        def nornir_filter():
            return F(name='R1')
            
        def test_basic_task(general_result):
            assert 'R1' in general_result
            assert 'R2' not in general_result
        """
    )

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.usefixtures("default_nr_init", "nr_wrapper")
def test_pass_nuts_arguments_to_nornir(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope="class")
        def nuts_task():
            return lambda task, arg: arg

        @pytest.fixture(scope="class")
        def nuts_arguments():
            return {'arg': 'testArgument'}

        def test_basic_task(general_result):
            assert general_result['R1'].result == 'testArgument'
        """
    )

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
