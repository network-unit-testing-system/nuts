import pytest
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_bgp_neighbors import CONTEXT
from nornir_napalm.plugins import tasks

from tests.utils import create_multi_result, SelfTestData

R1_IP = "172.16.255.1"
R2_IP = "172.16.255.2"
R3_IP = "172.16.255.3"

AS1 = 45001
AS2 = 45002
AS3 = 45003

AS_ID = "0.0.0.0"

nornir_raw_r1 = {
    "bgp_neighbors": {
        "global": {
            "router_id": R1_IP,
            "peers": {
                R2_IP: {
                    "local_as": AS1,
                    "remote_as": AS2,
                    "remote_id": AS_ID,
                    "is_up": False,
                    "is_enabled": True,
                    "description": "",
                    "uptime": -1,
                    "address_family": {
                        "ipv4 unicast": {
                            "received_prefixes": -1,
                            "accepted_prefixes": -1,
                            "sent_prefixes": -1,
                        }
                    },
                },
                R3_IP: {
                    "local_as": AS1,
                    "remote_as": AS3,
                    "remote_id": AS_ID,
                    "is_up": False,
                    "is_enabled": True,
                    "description": "",
                    "uptime": -1,
                    "address_family": {
                        "ipv4 unicast": {
                            "received_prefixes": -1,
                            "accepted_prefixes": -1,
                            "sent_prefixes": -1,
                        }
                    },
                },
            },
        }
    }
}

nornir_raw_r2 = {
    "bgp_neighbors": {
        "global": {
            "router_id": R2_IP,
            "peers": {
                R1_IP: {
                    "local_as": AS2,
                    "remote_as": AS1,
                    "remote_id": AS_ID,
                    "is_up": False,
                    "is_enabled": True,
                    "description": "",
                    "uptime": -1,
                    "address_family": {
                        "ipv4 unicast": {
                            "received_prefixes": -1,
                            "accepted_prefixes": -1,
                            "sent_prefixes": -1,
                        }
                    },
                }
            },
        }
    }
}

nornir_raw_r1_vrf = {
    "bgp_neighbors": {"CustA": nornir_raw_r1["bgp_neighbors"]["global"]}
}

nornir_raw_r2_vrf = {
    "bgp_neighbors": {"CustA": nornir_raw_r2["bgp_neighbors"]["global"]}
}

bgp_r1_1 = SelfTestData(
    name="r1_1",
    nornir_raw_result=nornir_raw_r1,
    test_data={
        "host": "R1",
        "local_id": R1_IP,
        "peer": R2_IP,
        "is_enabled": True,
        "remote_as": AS2,
        "remote_id": AS_ID,
        "local_as": AS1,
        "is_up": False,
    },
)

bgp_r1_2 = SelfTestData(
    name="r1_2",
    nornir_raw_result=nornir_raw_r1,
    test_data={
        "host": "R1",
        "local_id": R1_IP,
        "peer": R3_IP,
        "is_enabled": True,
        "remote_as": AS3,
        "remote_id": AS_ID,
        "local_as": AS1,
        "is_up": False,
    },
)

bgp_r2 = SelfTestData(
    name="r2",
    nornir_raw_result=nornir_raw_r2,
    test_data={
        "host": "R2",
        "local_id": R2_IP,
        "peer": R1_IP,
        "is_enabled": True,
        "remote_as": AS1,
        "remote_id": AS_ID,
        "local_as": AS2,
        "is_up": False,
    },
)

bgp_r2_vrf = SelfTestData(
    name="r2",
    nornir_raw_result=nornir_raw_r2_vrf,
    test_data={
        "host": "R2",
        "local_id": R2_IP,
        "peer": R1_IP,
        "is_enabled": True,
        "remote_as": AS1,
        "remote_id": AS_ID,
        "local_as": AS2,
        "is_up": False,
    },
)

bgp_r1_count = SelfTestData(
    name="r1_count",
    nornir_raw_result=nornir_raw_r1,
    test_data={
        "host": "R1",
        "neighbor_count": 2,
    },
)

bgp_r2_count = SelfTestData(
    name="r2_count",
    nornir_raw_result=nornir_raw_r2,
    test_data={
        "host": "R2",
        "neighbor_count": 1,
    },
)

bgp_r1_count_vrf = SelfTestData(
    name="r1_count",
    nornir_raw_result=nornir_raw_r1_vrf,
    test_data={
        "host": "R1",
        "neighbor_count": 2,
    },
)

bgp_r2_count_vrf = SelfTestData(
    name="r2_count",
    nornir_raw_result=nornir_raw_r2_vrf,
    test_data={
        "host": "R2",
        "neighbor_count": 1,
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result(
        results=[bgp_r1_1.create_nornir_result(), bgp_r1_2.create_nornir_result()],
        task_name=task_name,
    )
    result["R2"] = create_multi_result(
        results=[bgp_r2.create_nornir_result()], task_name=task_name
    )
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[
        bgp_r1_1,
        bgp_r1_2,
        bgp_r2,
    ],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture(
    params=[
        bgp_r2_vrf,
    ],
    ids=lambda data: data.name,
)
def selftestdata_vrf(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


@pytest.fixture(
    params=[bgp_r1_count, bgp_r2_count],
    ids=lambda data: data.name,
)
def selftestdata_countneighbors(request):
    return request.param


@pytest.fixture(
    params=[bgp_r1_count_vrf, bgp_r2_count_vrf],
    ids=lambda data: data.name,
)
def selftestdata_countneighbors_vrf(request):
    return request.param


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_hosts_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


@pytest.mark.parametrize("host, neighbors", [("R1", {R2_IP, R3_IP}), ("R2", {R1_IP})])
def test_contains_peers_at_second_level(transformed_result, host, neighbors):
    host_result = transformed_result[host]
    host_result.validate()
    assert host_result.result.keys() == neighbors


def test_contains_information_about_neighbor(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    neighbor_details = host_result.result[testdata["peer"]]
    expected = {
        "is_enabled": testdata["is_enabled"],
        "is_up": testdata["is_up"],
        "local_as": testdata["local_as"],
        "local_id": testdata["local_id"],
        "remote_as": testdata["remote_as"],
        "remote_id": testdata["remote_id"],
        "address_family": {
            "ipv4 unicast": {
                "accepted_prefixes": -1,
                "received_prefixes": -1,
                "sent_prefixes": -1,
            }
        },
        "description": "",
        "uptime": -1,
    }
    assert neighbor_details == expected


@pytest.mark.parametrize("host, neighbor_amount", [("R1", 2), ("R2", 1)])
def test_contains_correct_amount_of_hosts(transformed_result, host, neighbor_amount):
    host_result = transformed_result[host]
    host_result.validate()
    assert len(host_result.result) == neighbor_amount


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmBgpNeighbors",
        task_module=tasks,
        task_name="napalm_get",
        test_count=6,
    )


def test_integration_vrf(selftestdata_vrf, integration_tester):
    integration_tester(
        selftestdata_vrf,
        test_class="TestNapalmBgpNeighbors",
        task_module=tasks,
        test_execution={"vrf": "CustA"},
        task_name="napalm_get",
        test_count=6,
    )


def test_integration_count(selftestdata_countneighbors, integration_tester):
    integration_tester(
        selftestdata_countneighbors,
        test_class="TestNapalmBgpNeighborsCount",
        task_module=tasks,
        task_name="napalm_get",
        test_count=1,
    )


def test_integration_count_vrf(selftestdata_countneighbors_vrf, integration_tester):
    integration_tester(
        selftestdata_countneighbors_vrf,
        test_class="TestNapalmBgpNeighborsCount",
        task_module=tasks,
        test_execution={"vrf": "CustA"},
        task_name="napalm_get",
        test_count=1,
    )
