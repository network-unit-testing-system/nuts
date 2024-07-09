from typing import Dict, Any

import yaml
import pytest
from pytest import FixtureRequest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult

from nuts.context import NornirNutsContext, NutsContext

from tests.utils import create_multi_result, create_result, YAML_EXTENSION


TIMEOUT_MESSAGE = r"""Traceback (most recent call last):
  File "C:\somepath\lib\site-packages\netmiko\base_connection.py", line 920, in establish_connection
    self.remote_conn_pre.connect(**ssh_connect_params)
  File "C:\somepath\lib\site-packages\paramiko\client.py", line 349, in connect
    retry_on_signal(lambda: sock.connect(addr))
  File "C:\somepath\lib\site-packages\paramiko\util.py", line 283, in retry_on_signal
    return function()
  File "C:\somepath\lib\site-packages\paramiko\client.py", line 349, in <lambda>
    retry_on_signal(lambda: sock.connect(addr))
socket.timeout: timed out

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\somepath\lib\site-packages\napalm\base\base.py", line 92, in _netmiko_open
    **netmiko_optional_args
  File "C:\somepath\lib\site-packages\netmiko\ssh_dispatcher.py", line 312, in ConnectHandler
    return ConnectionClass(*args, **kwargs)
  File "C:\somepath\lib\site-packages\netmiko\cisco\cisco_ios.py", line 17, in __init__
    return super().__init__(*args, **kwargs)
  File "C:\somepath\lib\site-packages\netmiko\base_connection.py", line 346, in __init__
    self._open()
  File "C:\somepath\lib\site-packages\netmiko\base_connection.py", line 351, in _open
    self.establish_connection()
  File "C:\somepath\lib\site-packages\netmiko\base_connection.py", line 942, in establish_connection
    raise NetmikoTimeoutException(msg)
netmiko.ssh_exception.NetmikoTimeoutException: TCP connection to device failed.

Common causes of this problem are:
1. Incorrect hostname or IP address.
2. Wrong TCP port.
3. Intermediate firewall blocking access.

Device settings: cisco_ios 10.20.0.123:22



During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\somepath\lib\site-packages\nornir\core\task.py", line 98, in start
    r = self.task(self, **self.params)
  File "C:\somepath\lib\site-packages\nornir_napalm\plugins\tasks\napalm_get.py", line 32, in napalm_get
    device = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
  File "C:\somepath\lib\site-packages\nornir\core\inventory.py", line 448, in get_connection
    extras=conn.extras,
  File "C:\somepath\lib\site-packages\nornir\core\inventory.py", line 499, in open_connection
    configuration=configuration,
  File "C:\somepath\lib\site-packages\nornir_napalm\plugins\connections\__init__.py", line 57, in open
    connection.open()
  File "C:\somepath\lib\site-packages\napalm\ios\ios.py", line 170, in open
    device_type, netmiko_optional_args=self.netmiko_optional_args
  File "C:\somepath\lib\site-packages\napalm\base\base.py", line 95, in _netmiko_open
    raise ConnectionException("Cannot connect to {}".format(self.hostname))
napalm.base.exceptions.ConnectionException: Cannot connect to 10.20.0.123
"""  # noqa: E501


@pytest.fixture
def timeouted_multiresult():
    task_name = "failed_task"
    r = create_result(
        TIMEOUT_MESSAGE,
        failed=True,
        exception=ConnectionException("Cannot connect to 1.2.3.4"),
    )
    return create_multi_result([r], task_name=task_name)


@pytest.fixture
def test_ctx(request: FixtureRequest) -> NutsContext:
    """
    Enable every test to use its specific context class.
    Uses a custom pytest marker that is set on a test module level,
    visible in the tests as:
        pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]

    See also:
    https://docs.pytest.org/en/stable/example/markers.html#marking-whole-classes-or-modules
    :param request: The request for the fixture
    :return: The initialized NutsContext
    """
    marker = request.node.get_closest_marker("nuts_test_ctx")
    if marker is None:
        raise pytest.UsageError("Custom nuts_test_ctx marker not found")
    return marker.args[0]


@pytest.fixture
def transformed_result(
    test_ctx: NornirNutsContext, general_result: AggregatedResult
) -> Dict[str, Any]:
    """
    Parse the raw result to be used in nuts tests.
    :param test_ctx: initialized NutsContext
    :param general_result: mock raw answer that is normally provided by nornir
    :return: Dict with host as keys, `NutsResult` as values
    """
    return test_ctx.extractor.transform_result(general_result)


@pytest.fixture
def integration_tester(monkeypatch, pytester, default_nr_init):
    def _run(
        selftestdata,
        *,
        test_class,
        task_module,
        task_name,
        test_count,
        test_execution=None,
    ):
        yaml_data = [
            {
                "test_class": test_class,
                "test_data": [selftestdata.test_data],
            }
        ]
        if test_execution:
            yaml_data[0]["test_execution"] = test_execution

        yaml_file = pytester.path / f"test{YAML_EXTENSION}"
        with yaml_file.open("w") as fo:
            yaml.dump(yaml_data, fo)

        monkeypatch.setattr(
            task_module,
            task_name,
            lambda *args, **kwargs: selftestdata.nornir_raw_result,
        )

        res = pytester.runpytest_inprocess()

        if selftestdata.expected_output is not None:
            res.stdout.fnmatch_lines(selftestdata.expected_output)

        res.assert_outcomes(**{selftestdata.expected_outcome: test_count})

    return _run
