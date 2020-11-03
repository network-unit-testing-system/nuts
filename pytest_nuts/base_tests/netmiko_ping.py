from pytest_nuts.nuts_netmiko_ping import *


class TestNetmikoPing:

    @pytest.fixture(scope="class")
    def nuts_task(self):
        return netmiko_ping_multi_host

    @pytest.fixture(scope="class")
    def nuts_arguments(self, nuts_parameters):
        test_data = nuts_parameters['test_data']
        delay_factor = nuts_parameters['test_execution']['delay_factor']
        return {"destinations_per_host": destinations_per_host(test_data),
                "delay_factor": delay_factor}

    @pytest.fixture(scope="class")
    def hosts(self, test_execution_params):
        return {entry["source"] for entry in test_execution_params}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        raw_textfsm_pinganswer = {key: [v.result for v in value[1:]] for key, value in general_result.items()}
        return {key: parse_ping_results(value) for key, value in raw_textfsm_pinganswer.items()}

    @pytest.fixture(scope="class")
    def test_execution_params(self, nuts_parameters):
        return nuts_parameters['test_data']

    @pytest.mark.nuts("source,destination,expected", "placeholder")
    def test_ping(self, transformed_result, source, destination, expected):
        assert transformed_result[source][destination].name == expected
