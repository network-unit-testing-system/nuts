class TestCase:
    def __init__(self, name, command, devices, parameter, operator, expected_result):
        self.name = name
        self.command = command
        self.devices = devices
        self.parameter = parameter
        self.operator = operator
        self.expected_result = expected_result
        self.job_id = ''
        self.minions = []

    def set_actual_result(self, actual_result):
        self.actual_result = actual_result

    def get_actual_result(self):
        return self.actual_result

    def set_job(self, job_description):
        self.job_id = job_description['return'][0]['jid']
        self.minions = job_description['return'][0]['minions']

    def __str__(self):
        return "Name: {0}, Command: {1}, Devices: {2}, Parameter: {3}, Operator: {4}, Expected: {5}".format(self.name,
                                                                                                            self.command,
                                                                                                            self.devices,
                                                                                                            self.parameter,
                                                                                                            self.operator,
                                                                                                            self.expected_result)
