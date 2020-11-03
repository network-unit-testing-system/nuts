from enum import Enum

from nornir.core import Task
from nornir.core.task import MultiResult
from nornir_netmiko.tasks import netmiko_send_command

import pytest


class Ping(Enum):
    FAIL = 0
    SUCCESS = 1
    FLAPPING = 2


def parse_ping_results(raw_result):
    parsed_results = {}
    for item in raw_result:
        # TODO unstable parsing - add logger here to print raw result before parsing
        # if the host is unreachable, the current parsing is unstable and sometimes has the correct
        # Ping.FAIL, sometimes the wrong Ping.FLAPPING
        print(f"Raw result: {item}")
        dest = item.partition("Echos to ")[2].partition(", timeout is")[0]
        if "Success rate is 100 percent (5/5)" in item:
            parsed_results[dest] = Ping.SUCCESS
        elif "Success rate is 0 percent (0/5)" in item:
            parsed_results[dest] = Ping.FAIL
        else:
            parsed_results[dest] = Ping.FLAPPING
    return parsed_results


def netmiko_ping_multi_host(task: Task, destinations_per_host, delay_factor=5) -> MultiResult:
    print(f"starting netmiko_ping_multi_host on {task.host.name}")
    destinations = destinations_per_host(task.host.name)
    print(f'{task.host.name}: {destinations}')
    results = MultiResult("pinged_hosts")
    for destination in destinations:
        results.append(
            task.run(
                task=netmiko_send_command,
                command_string=f"ping {destination}",
                use_textfsm=True,
                delay_factor=delay_factor
            )
        )
    return results


def destinations_per_host(test_data):
    return lambda host_name: [entry["destination"] for entry in test_data if entry["source"] == host_name]

#
# @pytest.fixture(scope="class")
# def nuts_task():
#     return netmiko_ping_multi_host
# 
# @pytest.fixture(scope="class")
# def nuts_arguments(test_topology_data):
#     return {"destinations_per_host": destinations_per_host(test_topology_data)}
#
#
# @pytest.fixture(scope="class")
# def hosts(test_topology_data):
#     return {entry["source"] for entry in test_topology_data}
#
#
# @pytest.fixture(scope="class")
# def transformed_result(general_result):
#     raw_textfsm_pinganswer = {key: [v.result for v in value[1:]] for key, value in general_result.items()}
#     return {key: parse_ping_results(value) for key, value in raw_textfsm_pinganswer.items()}
