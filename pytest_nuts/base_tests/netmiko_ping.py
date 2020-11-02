from pytest_nuts.netmiko_ping import *


class TestNetmikoPing:

    @pytest.fixture(scope="class")
    def nuts_task(self):
        return netmiko_ping_multi_host

    @pytest.fixture(scope="class")
    def nuts_arguments(self, destination_list):
        return {"destinations_per_host": destinations_per_host(destination_list),
                "delay_factor": 2}

    @pytest.fixture(scope="class")
    def hosts(self, destination_list):
        return {entry["source"] for entry in destination_list}

    @pytest.fixture(scope="class")
    def transformed_result(self, general_result):
        raw_textfsm_pinganswer = {key: [v.result for v in value[1:]] for key, value in general_result.items()}
        return {key: parse_ping_results(value) for key, value in raw_textfsm_pinganswer.items()}

    @pytest.fixture(scope="class")
    def destination_list(self, nuts_parameters):
        return nuts_parameters['arguments']

    @pytest.mark.nuts("source,destination,expected", "placeholder")
    def test_ping(self, transformed_result, source, destination, expected):
        assert transformed_result[source][destination].name == expected
