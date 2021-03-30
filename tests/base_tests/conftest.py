import pytest
from _pytest.fixtures import FixtureRequest
from napalm.base.exceptions import ConnectionException
from pytest_nuts.context import NornirNutsContext, NutsContext

from tests.helpers.shared import create_multi_result

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
"""


@pytest.fixture
def timeouted_multiresult():
    return create_multi_result(
        TIMEOUT_MESSAGE,
        failed=True,
        exception=ConnectionException("Cannot connect to 10.20.0.123"),
    )


@pytest.fixture
def test_ctx(request: FixtureRequest):
    marker = request.node.get_closest_marker("nuts_test_ctx")
    if marker is None:
        raise pytest.UsageError("custom nuts_test_ctx marker not found")
    # intentionally do not use marker.arg[0] because of this: https://github.com/pytest-dev/pytest/issues/8499
    # pytest.marker.with_args() also intentionally not used here, because it can be forgotten
    # https://docs.pytest.org/en/stable/example/markers.html#passing-a-callable-to-custom-markers
    return marker.kwargs["context"]


@pytest.fixture
def transformed_result(test_ctx: NornirNutsContext, general_result):
    ctx = test_ctx(nuts_parameters=None)
    return ctx.transform_result(general_result)
