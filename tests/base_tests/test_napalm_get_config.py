import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_get_config import CONTEXT

from tests.utils import create_multi_result, SelfTestData


nornir_raw_result_s1 = {
    "config": {
        "startup": "!\n"
        "\n"
        "!\n"
        "version 15.2\n"
        "service timestamps debug datetime msec\n"
        "service timestamps log datetime msec\n"
        "no service password-encryption\n"
        "service compress-config\n"
        "!\n"
        "hostname viosswitch-1\n"
        "!\n"
        "boot-start-marker\n"
        "boot-end-marker\n"
        "!\n"
        "!\n"
        "vrf definition mgmt\n"
        " !\n"
        " address-family ipv4\n"
        " exit-address-family\n"
        "!\n"
        "!\n"
        "username cisco privilege 15 password 0 cisco\n"
        "no aaa new-model\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "no ip domain-lookup\n"
        "ip domain-name lab\n"
        "ip cef\n"
        "no ipv6 cef\n"
        "!\n"
        "!\n"
        "archive\n"
        " path flash:backup\n"
        " write-memory\n"
        "!\n"
        "spanning-tree mode pvst\n"
        "spanning-tree extend system-id\n"
        "!\n"
        "vlan internal allocation policy ascending\n"
        "!\n"
        "! \n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "interface GigabitEthernet0/0\n"
        " description OOB-Mgmt\n"
        " no switchport\n"
        " vrf forwarding mgmt\n"
        " ip address "
        "dhcp\n"
        " negotiation auto\n"
        " no cdp enable\n"
        "!\n"
        "interface GigabitEthernet0/1\n"
        " description R3\n"
        " switchport "
        "trunk encapsulation dot1q\n"
        " switchport mode trunk\n"
        " media-type rj45\n"
        " negotiation auto\n"
        "!\n"
        "interface GigabitEthernet0/2\n"
        " description sw01\n"
        " switchport trunk encapsulation dot1q\n"
        " switchport mode trunk\n"
        " media-type rj45\n"
        " negotiation auto\n"
        "!\n"
        "interface GigabitEthernet0/3\n"
        " description client\n"
        " media-type rj45\n"
        " negotiation auto\n"
        "!\n"
        "interface Vlan1\n"
        " ip address 10.0.0.110 255.255.255.0\n"
        "!\n"
        "interface Vlan200\n"
        " ip address 10.0.200.110 255.255.255.0\n"
        "!\n"
        "ip forward-protocol nd\n"
        "!\n"
        "no ip http server\n"
        "no ip http secure-server\n"
        "!\n"
        "ip ssh version 2\n"
        "ip scp server enable\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "control-plane\n"
        "!\n"
        "banner exec ^C\n"
        "**************************************************************************\n"
        "* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n"
        "* education. IOSv is provided as-is and is not supported by Cisco's      *\n"
        "* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n"
        "* of the IOSv Software or Documentation to any third party for any       *\n"
        "* purposes is expressly prohibited except as otherwise authorized by     *\n"
        "* Cisco in writing.                                                      *\n"
        "**************************************************************************^C\n"
        "banner incoming ^C\n"
        "**************************************************************************\n"
        "* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n"
        "* education. IOSv is provided as-is and is not supported by Cisco's      *\n"
        "* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n"
        "* of the IOSv Software or Documentation to any third party for any       *\n"
        "* purposes is expressly prohibited except as otherwise authorized by     *\n"
        "* Cisco in writing.                                                      *\n"
        "**************************************************************************^C\n"
        "banner login ^C\n"
        "**************************************************************************\n"
        "* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n"
        "* education. IOSv is provided as-is and is not supported by Cisco's      *\n"
        "* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n"
        "* of the IOSv Software or Documentation to any third party for any       *\n"
        "* purposes is expressly prohibited except as otherwise authorized by     *\n"
        "* Cisco in writing.                                                      *\n"
        "**************************************************************************^C\n"
        "!\n"
        "line con 0\n"
        "line aux 0\n"
        "line vty 0 4\n"
        " login local\n"
        "line vty 5 15\n"
        " login local\n"
        "!\n"
        "ntp server pnpntpserver.ins.local\n"
        "!\n"
        "end",
        "running": "!\n"
        "\n"
        "!\n"
        "version 15.2\n"
        "service timestamps debug datetime msec\n"
        "service timestamps log datetime msec\n"
        "no service password-encryption\n"
        "service compress-config\n"
        "!\n"
        "hostname viosswitch-1\n"
        "!\n"
        "boot-start-marker\n"
        "boot-end-marker\n"
        "!\n"
        "!\n"
        "vrf definition mgmt\n"
        " !\n"
        " address-family ipv4\n "
        "exit-address-family\n"
        "!\n"
        "!\n"
        "username cisco privilege 15 password 0 cisco\n"
        "no aaa new-model\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "no ip domain-lookup\n"
        "ip domain-name lab\n"
        "ip cef\n"
        "no ipv6 cef\n"
        "!\n"
        "!\n"
        "archive\n"
        " path flash:backup\n"
        " write-memory\n"
        "!\n"
        "spanning-tree mode pvst\n"
        "spanning-tree extend system-id\n"
        "!\n"
        "vlan internal allocation policy ascending\n"
        "!\n"
        "! \n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "interface GigabitEthernet0/0\n"
        " description OOB-Mgmt\n"
        " no switchport\n"
        " vrf forwarding mgmt\n"
        " ip address dhcp\n"
        " negotiation auto\n"
        " no cdp enable\n"
        "!\n"
        "interface GigabitEthernet0/1\n"
        " description R3\n"
        " switchport trunk encapsulation dot1q\n"
        " switchport mode trunk\n"
        " media-type rj45\n"
        " negotiation auto\n"
        "!\n"
        "interface GigabitEthernet0/2\n"
        " description sw01\n"
        " switchport trunk encapsulation dot1q\n"
        " switchport mode trunk\n"
        " media-type rj45\n"
        " negotiation auto\n"
        "!\n"
        "interface GigabitEthernet0/3\n"
        " description client\n"
        " media-type rj45\n"
        " negotiation auto\n"
        "!\n"
        "interface Vlan1\n"
        " ip address 10.0.0.110 255.255.255.0\n"
        "!\n"
        "interface Vlan200\n"
        " ip address 10.0.200.110 255.255.255.0\n"
        "!\n"
        "ip forward-protocol nd\n"
        "!\n"
        "no ip http server\n"
        "no ip http secure-server\n"
        "!\n"
        "ip ssh version 2\n"
        "ip scp server enable\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "!\n"
        "control-plane\n"
        "!\n"
        "banner exec ^C\n"
        "**************************************************************************\n"
        "* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n"
        "* education. IOSv is provided as-is and is not supported by Cisco's      *\n"
        "* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n"
        "* of the IOSv Software or Documentation to any third party for any       *\n"
        "* purposes is expressly prohibited except as otherwise authorized by     *\n"
        "* Cisco in writing.                                                      *\n"
        "**************************************************************************^C\n"
        "banner incoming ^C\n"
        "**************************************************************************\n"
        "* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n"
        "* education. IOSv is provided as-is and is not supported by Cisco's      *\n"
        "* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n"
        "* of the IOSv Software or Documentation to any third party for any       *\n"
        "* purposes is expressly prohibited except as otherwise authorized by     *\n"
        "* Cisco in writing.                                                      *\n"
        "**************************************************************************^C\n"
        "banner login ^C\n"
        "**************************************************************************\n"
        "* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n"
        "* education. IOSv is provided as-is and is not supported by Cisco's      *\n"
        "* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n"
        "* of the IOSv Software or Documentation to any third party for any       *\n"
        "* purposes is expressly prohibited except as otherwise authorized by     *\n"
        "* Cisco in writing.                                                      *\n"
        "**************************************************************************^C\n"
        "!\n"
        "line con 0\n"
        "line aux 0\n"
        "line vty 0 4\n"
        " login local\n"
        "line vty 5 15\n"
        " login local\n"
        "!\n"
        "ntp server pnpntpserver.ins.local\n"
        "!\n"
        "end",
        "candidate": "",
    }
}

nornir_raw_result_s2 = {
    "config": {
        "startup": "! Command: show startup-config\n"
        "! Startup-config last modified at Fri Jul 12 15:59:25 2024 by root\n"
        "! device: fra05-pod1-leaf1 (cEOSLab, EOS-4.28.9M-33818481.4289M"
        "(engineering build))\n"
        "!\nno aaa root\n!\nusername admin privilege 15 role redistribute connected\n"
        "   network 0.0.0.0/0 area 0.0.0.0\n   max-lsa 12000\n!\nend\n'",
        "running": "! Command: show running-config\n"
        "! device: fra05-pod1-leaf1 (cEOSLab, EOS-4.28.9M-33818481.4289M"
        "(engineering build))\n"
        "!\nno aaa root\n!\nusername admin privilege 15 role redistribute connected\n"
        "   network 0.0.0.0/0 area 0.0.0.0\n   max-lsa 12000\n!\nend\n'",
    }
}


config_s1 = SelfTestData(
    name="s1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "startup_equals_running_config": True},
)

config_s2 = SelfTestData(
    name="s2",
    nornir_raw_result=nornir_raw_result_s2,
    test_data={"host": "S2", "startup_equals_running_config": True},
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "napalm_get_facts"
    result = AggregatedResult(task_name)
    result["S1"] = create_multi_result(
        [config_s1.create_nornir_result()],
        task_name,
    )
    result["S3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[config_s1, config_s2],
    ids=lambda data: data.name,
)
def selftestdata(request):
    return request.param


@pytest.fixture
def testdata(selftestdata):
    return selftestdata.test_data


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


@pytest.fixture
def single_result(transformed_result, testdata):
    host_result = transformed_result[testdata["host"]]
    host_result.validate()
    return host_result.result


def test_startup_equals_running_config_isBoolean(testdata):
    assert isinstance(testdata["startup_equals_running_config"], bool)


def test_integration(selftestdata, integration_tester):
    integration_tester(
        selftestdata,
        test_class="TestNapalmConfig",
        task_module=tasks,
        task_name="napalm_get",
        test_count=1,
    )
