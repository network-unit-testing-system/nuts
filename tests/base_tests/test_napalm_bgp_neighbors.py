import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult

from pytest_nuts.base_tests.napalm_bgp_neighbors import transform_result
from tests.helpers.shared import create_multi_result

neighbor_details = {
    "local_as": 45001,
    "remote_as": 45002,
    "remote_id": "0.0.0.0",
    "is_up": False,
    "is_enabled": True,
    "description": "",
    "uptime": -1,
    "address_family": {"ipv4 unicast": {"received_prefixes": -1, "accepted_prefixes": -1, "sent_prefixes": -1}},
}


@pytest.fixture
def general_result():
    result = AggregatedResult("napalm_get")
    result["R1"] = create_multi_result(
        {
            "bgp_neighbors": {
                "global": {
                    "router_id": "172.16.255.1",
                    "peers": {
                        "172.16.255.2": neighbor_details.copy(),
                        "172.16.255.3": {
                            "local_as": 45001,
                            "remote_as": 45003,
                            "remote_id": "0.0.0.0",
                            "is_up": False,
                            "is_enabled": True,
                            "description": "",
                            "uptime": -1,
                            "address_family": {
                                "ipv4 unicast": {"received_prefixes": -1, "accepted_prefixes": -1, "sent_prefixes": -1}
                            },
                        },
                    },
                }
            }
        }
    )
    result["R2"] = create_multi_result(
        {
            "bgp_neighbors": {
                "global": {
                    "router_id": "172.16.255.2",
                    "peers": {
                        "172.16.255.1": {
                            "local_as": 45002,
                            "remote_as": 45001,
                            "remote_id": "0.0.0.0",
                            "is_up": False,
                            "is_enabled": True,
                            "description": "",
                            "uptime": -1,
                            "address_family": {
                                "ipv4 unicast": {"received_prefixes": -1, "accepted_prefixes": -1, "sent_prefixes": -1}
                            },
                        }
                    },
                }
            }
        }
    )

    result["R3"] = create_multi_result(
        r"""Traceback (most recent call last):
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\netmiko\base_connection.py", line 920, in establish_connection
    self.remote_conn_pre.connect(**ssh_connect_params)
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\paramiko\client.py", line 349, in connect
    retry_on_signal(lambda: sock.connect(addr))
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\paramiko\util.py", line 283, in retry_on_signal
    return function()
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\paramiko\client.py", line 349, in <lambda>
    retry_on_signal(lambda: sock.connect(addr))
socket.timeout: timed out

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\napalm\base\base.py", line 92, in _netmiko_open
    **netmiko_optional_args
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\netmiko\ssh_dispatcher.py", line 312, in ConnectHandler
    return ConnectionClass(*args, **kwargs)
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\netmiko\cisco\cisco_ios.py", line 17, in __init__
    return super().__init__(*args, **kwargs)
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\netmiko\base_connection.py", line 346, in __init__
    self._open()
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\netmiko\base_connection.py", line 351, in _open
    self.establish_connection()
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\netmiko\base_connection.py", line 942, in establish_connection
    raise NetmikoTimeoutException(msg)
netmiko.ssh_exception.NetmikoTimeoutException: TCP connection to device failed.

Common causes of this problem are:
1. Incorrect hostname or IP address.
2. Wrong TCP port.
3. Intermediate firewall blocking access.

Device settings: cisco_ios 10.20.0.123:22



During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\nornir\core\task.py", line 98, in start
    r = self.task(self, **self.params)
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\nornir_napalm\plugins\tasks\napalm_get.py", line 32, in napalm_get
    device = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\nornir\core\inventory.py", line 448, in get_connection
    extras=conn.extras,
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\nornir\core\inventory.py", line 499, in open_connection
    configuration=configuration,
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\nornir_napalm\plugins\connections\__init__.py", line 57, in open
    connection.open()
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\napalm\ios\ios.py", line 170, in open
    device_type, netmiko_optional_args=self.netmiko_optional_args
  File "C:\Users\maede\Documents\nornir-pytest-playground\venv\lib\site-packages\napalm\base\base.py", line 95, in _netmiko_open
    raise ConnectionException("Cannot connect to {}".format(self.hostname))
napalm.base.exceptions.ConnectionException: Cannot connect to 10.20.0.123
""",
        failed=True,
        exception=ConnectionException("Cannot connect to 10.20.0.123"),
    )
    return result


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2", "R3"])
    def test_contains_hosts_at_toplevel(self, general_result, host):
        transformed_result = transform_result(general_result)
        assert host in transformed_result

    @pytest.mark.parametrize("host,neighbors", [("R1", ["172.16.255.2", "172.16.255.3"]), ("R2", ["172.16.255.1"])])
    def test_contains_peers_at_second_level(self, general_result, host, neighbors):
        transformed_result = transform_result(general_result)
        assert list(transformed_result[host].result.keys()) == neighbors

    @pytest.mark.parametrize("host,neighbor,details", [("R1", "172.16.255.2", neighbor_details)])
    def test_contains_information_about_neighbor(self, general_result, host, neighbor, details):
        transformed_result = transform_result(general_result)
        expected_details = transformed_result[host].result[neighbor]
        for key in details:
            assert expected_details[key] == details[key]

    @pytest.mark.parametrize("host,neighbor,local_id", [("R1", "172.16.255.2", "172.16.255.1")])
    def test_contains_router_id_as_local_id(self, general_result, host, neighbor, local_id):
        transformed_result = transform_result(general_result)
        assert transformed_result[host].result[neighbor]["local_id"] == local_id

    def test_marks_as_failed_if_task_failed(self, general_result):
        transformed_result = transform_result(general_result)
        assert transformed_result["R3"].failed
        assert transformed_result["R3"].exception is not None