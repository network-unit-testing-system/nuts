from __future__ import absolute_import
from __future__ import unicode_literals


class TestCase(object):
    def __init__(self, name, command, devices, parameter, operator, expected, setup=[], teardown=[]):
        self.name = name
        self.command = command
        self.devices = devices
        self.parameter = parameter
        self.operator = operator
        self.expected_result = expected
        self.setup_tasks = setup
        self.teardown_tasks = teardown
        self.job_id = ''
        self.minions = []
        self.actual_result = None
        self.saved_data = {}

    def set_actual_result(self, actual_result):
        self.actual_result = actual_result

    def get_actual_result(self):
        return self.actual_result

    def extract_actual_result(self):
        return {k: v['result'] for k, v in self.actual_result.items()}

    def set_job(self, jid):
        self.job_id = jid

    def set_minions(self, minion_list):
        self.minions = minion_list

    def __str__(self):
        return 'Name: {0}, Command: {1}, Devices: {2}, Parameter: {3}, Operator: {4}, Expected: {5}' \
            .format(self.name, self.command, self.devices, self.parameter, self.operator, self.expected_result)
