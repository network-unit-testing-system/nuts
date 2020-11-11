import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from pytest_nuts.base_tests.napalm_ping import transform_result

test_data = [{
        "expected": "SUCCESS",
        "source": "R1",
        "destination": "172.16.23.3",
        "max_drop": 1
        },
        {
        "expected": "SUCCESS",
        "source": "R2",
        "destination": "172.16.23.3",
        "max_drop": 1
      }]

@pytest.fixture
def general_result():
    result = AggregatedResult("napalm_get")
    multi_result_r1 = MultiResult("napalm_get")
    result_r1 = Result(host=None, name="napalm_get")
    result_r1.result = {
        {'success': {'probes_sent': 5, 'packet_loss': 0, 'rtt_min': 1.0, 'rtt_max': 2.0, 'rtt_avg': 1.0,
                     'rtt_stddev': 0.0,
                     'results': [{'ip_address': '172.16.23.3', 'rtt': 0.0}, {'ip_address': '172.16.23.3', 'rtt': 0.0},
                                 {'ip_address': '172.16.23.3', 'rtt': 0.0}, {'ip_address': '172.16.23.3', 'rtt': 0.0},
                                 {'ip_address': '172.16.23.3', 'rtt': 0.0}]}}
    }
    multi_result_r1.append(result_r1)
    result["R1"] = multi_result_r1
    multi_result_r2 = MultiResult("napalm_get")
    result_r2 = Result(host=None, name="napalm_get")
    result_r2.result = {
        {'success': {'probes_sent': 5, 'packet_loss': 0, 'rtt_min': 1.0, 'rtt_max': 1.0, 'rtt_avg': 1.0,
                     'rtt_stddev': 0.0,
                     'results': [{'ip_address': '172.16.23.3', 'rtt': 0.0}, {'ip_address': '172.16.23.3', 'rtt': 0.0},
                                 {'ip_address': '172.16.23.3', 'rtt': 0.0}, {'ip_address': '172.16.23.3', 'rtt': 0.0},
                                 {'ip_address': '172.16.23.3', 'rtt': 0.0}]}}
    }
    multi_result_r2.append(result_r2)
    result["R2"] = multi_result_r2
    return result


class TestTransformResult:
    @pytest.mark.parametrize("host", ["R1", "R2"])
    def test_contains_host_at_toplevel(self, general_result, host):
        transformed_result = transform_result(general_result, test_data)
        assert host in transformed_result

    @pytest.mark.parametrize("host,destination", [("R1", "172.16.23.3"), ("R2", "172.16.23.3")])
    def test_contains_pingeddestination(self, general_result, host, destination):
        transformed_result = transform_result(general_result, test_data)
        assert transformed_result[host].keys == destination  # assert keys

    @pytest.mark.parametrize("host,destination,ping_result",[("R1", "172.16.23.3", 1), ("R2", "172.16.23.3", 1)] )
    def test_destination_maps_to_enum(self, general_result, host, destination, ping_result):
        transformed_result = transform_result(general_result, test_data)
        assert transformed_result[host][destination]

    # results-part is not empty and contains ip-addresses
        # was transform_result zurückgibt:
        result = {'R1': {
                   '172.16.23.3': SUCCESS: 1 >, '172.16.14.4': < Ping.SUCCESS: 1 >, '172.16.42.42': < Ping.FAIL: 0 >},
        'R2': {'172.16.23.3': < Ping.SUCCESS: 1 >, '172.16.14.4': < Ping.SUCCESS: 1 >, '172.16.42.43': < Ping.FAIL: 0 >}
        }
    #
