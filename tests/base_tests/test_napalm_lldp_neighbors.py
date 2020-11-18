import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult

from pytest_nuts.base_tests.napalm_lldp_neighbors import transform_result
from tests.shared import create_multi_result

neighbor_details = {
    "remote_chassis_id": "001e.e611.3500",
    "remote_port": "Gi2",
    "remote_port_description": "test12345",
    "remote_system_name": "R3",
    "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
    "remote_system_capab": ["bridge", "router"],
    "remote_system_enable_capab": ["router"],
    "parent_interface": "",
}


@pytest.fixture
def general_result():
    result = AggregatedResult("napalm_get")
    result["R1"] = create_multi_result(
        {
            "lldp_neighbors_detail": {
                "GigabitEthernet4": [neighbor_details.copy()],
                "GigabitEthernet3": [
                    {
                        "remote_chassis_id": "001e.f62f.a600",
                        "remote_port": "Gi2",
                        "remote_port_description": "GigabitEthernet2",
                        "remote_system_name": "R2",
                        "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
                        "remote_system_capab": ["bridge", "router"],
                        "remote_system_enable_capab": ["router"],
                        "parent_interface": "",
                    }
                ],
            }
        }
    )
    result["R2"] = create_multi_result(
        {
            "lldp_neighbors_detail": {
                "GigabitEthernet4": [
                    {
                        "remote_chassis_id": "001e.e611.3500",
                        "remote_port": "Gi3",
                        "remote_port_description": "GigabitEthernet3",
                        "remote_system_name": "R3",
                        "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
                        "remote_system_capab": ["bridge", "router"],
                        "remote_system_enable_capab": ["router"],
                        "parent_interface": "",
                    }
                ],
                "GigabitEthernet2": [
                    {
                        "remote_chassis_id": "001e.e547.df00",
                        "remote_port": "Gi3",
                        "remote_port_description": "GigabitEthernet3",
                        "remote_system_name": "R1",
                        "remote_system_description": "Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.11.1a, RELEASE SOFTWARE (fc1)",
                        "remote_system_capab": ["bridge", "router"],
                        "remote_system_enable_capab": ["router"],
                        "parent_interface": "",
                    }
                ],
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

    @pytest.mark.parametrize(
        "host,local_ports",
        [("R1", ["GigabitEthernet4", "GigabitEthernet3"]), ("R2", ["GigabitEthernet4", "GigabitEthernet2"])],
    )
    def test_contains_results_with_ports_at_second_level(self, general_result, host, local_ports):
        transformed_result = transform_result(general_result)
        assert list(transformed_result[host].result.keys()) == local_ports

    @pytest.mark.parametrize(
        "host,local_ports",
        [("R3", ["GigabitEthernet4"])],
    )
    def test_contains_failed_result_at_second_level_if_task_failed(self, general_result, host, local_ports):
        transformed_result = transform_result(general_result)
        assert transformed_result[host].failed
        assert transformed_result[host].exception

    @pytest.mark.parametrize("host,local_port,expected_details", [("R1", "GigabitEthernet4", neighbor_details)])
    def test_contains_information_about_neighbor(self, general_result, host, local_port, expected_details):
        transformed_result = transform_result(general_result)
        actual_details = transformed_result[host].result[local_port]
        for key in expected_details:
            assert actual_details[key] == expected_details[key]

    @pytest.mark.parametrize("host,local_port,remote_host", [("R1", "GigabitEthernet4", "R3")])
    def test_contains_information_remote_host(self, general_result, host, local_port, remote_host):
        transformed_result = transform_result(general_result)
        assert transformed_result[host].result[local_port]["remote_host"] == remote_host

    @pytest.mark.parametrize("host,local_port,remote_port_expanded", [("R1", "GigabitEthernet4", "GigabitEthernet2")])
    def test_contains_information_expanded_interface(self, general_result, host, local_port, remote_port_expanded):
        transformed_result = transform_result(general_result)
        assert transformed_result[host].result[local_port]["remote_port_expanded"] == remote_port_expanded
