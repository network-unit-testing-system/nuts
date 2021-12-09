import pytest
from nornir.core.task import AggregatedResult
from nornir_napalm.plugins import tasks

from nuts.base_tests.napalm_get_config import CONTEXT

from tests.utils import create_multi_result, SelfTestData


nornir_raw_result_s1 = {
    "startup": "!\n\n!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nno service password-encryption\nservice compress-config\n!\nhostname viosswitch-1\n!\nboot-start-marker\nboot-end-marker\n!\n!\nvrf definition mgmt\n !\n address-family ipv4\n exit-address-family\n!\n!\nusername cisco privilege 15 password 0 cisco\nno aaa new-model\n!\n!\n!\n!\n!\n!\n!\n!\nno ip domain-lookup\nip domain-name lab\nip cef\nno ipv6 cef\n!\n!\narchive\n path flash:backup\n write-memory\n!\nspanning-tree mode pvst\nspanning-tree extend system-id\n!\nvlan internal allocation policy ascending\n!\n! \n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\ninterface GigabitEthernet0/0\n description OOB-Mgmt\n no switchport\n vrf forwarding mgmt\n ip address dhcp\n negotiation auto\n no cdp enable\n!\ninterface GigabitEthernet0/1\n description R3\n switchport trunk encapsulation dot1q\n switchport mode trunk\n media-type rj45\n negotiation auto\n!\ninterface GigabitEthernet0/2\n description sw01\n switchport trunk encapsulation dot1q\n switchport mode trunk\n media-type rj45\n negotiation auto\n!\ninterface GigabitEthernet0/3\n description client\n media-type rj45\n negotiation auto\n!\ninterface Vlan1\n ip address 10.0.0.110 255.255.255.0\n!\ninterface Vlan200\n ip address 10.0.200.110 255.255.255.0\n!\nip forward-protocol nd\n!\nno ip http server\nno ip http secure-server\n!\nip ssh version 2\nip scp server enable\n!\n!\n!\n!\n!\ncontrol-plane\n!\nbanner exec ^C\n**************************************************************************\n* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n* education. IOSv is provided as-is and is not supported by Cisco's      *\n* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n* of the IOSv Software or Documentation to any third party for any       *\n* purposes is expressly prohibited except as otherwise authorized by     *\n* Cisco in writing.                                                      *\n**************************************************************************^C\nbanner incoming ^C\n**************************************************************************\n* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n* education. IOSv is provided as-is and is not supported by Cisco's      *\n* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n* of the IOSv Software or Documentation to any third party for any       *\n* purposes is expressly prohibited except as otherwise authorized by     *\n* Cisco in writing.                                                      *\n**************************************************************************^C\nbanner login ^C\n**************************************************************************\n* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n* education. IOSv is provided as-is and is not supported by Cisco's      *\n* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n* of the IOSv Software or Documentation to any third party for any       *\n* purposes is expressly prohibited except as otherwise authorized by     *\n* Cisco in writing.                                                      *\n**************************************************************************^C\n!\nline con 0\nline aux 0\nline vty 0 4\n login local\nline vty 5 15\n login local\n!\nntp server pnpntpserver.ins.local\n!\nend",
    "running": "!\n\n!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nno service password-encryption\nservice compress-config\n!\nhostname viosswitch-1\n!\nboot-start-marker\nboot-end-marker\n!\n!\nvrf definition mgmt\n !\n address-family ipv4\n exit-address-family\n!\n!\nusername cisco privilege 15 password 0 cisco\nno aaa new-model\n!\n!\n!\n!\n!\n!\n!\n!\nno ip domain-lookup\nip domain-name lab\nip cef\nno ipv6 cef\n!\n!\narchive\n path flash:backup\n write-memory\n!\nspanning-tree mode pvst\nspanning-tree extend system-id\n!\nvlan internal allocation policy ascending\n!\n! \n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\ninterface GigabitEthernet0/0\n description OOB-Mgmt\n no switchport\n vrf forwarding mgmt\n ip address dhcp\n negotiation auto\n no cdp enable\n!\ninterface GigabitEthernet0/1\n description R3\n switchport trunk encapsulation dot1q\n switchport mode trunk\n media-type rj45\n negotiation auto\n!\ninterface GigabitEthernet0/2\n description sw01\n switchport trunk encapsulation dot1q\n switchport mode trunk\n media-type rj45\n negotiation auto\n!\ninterface GigabitEthernet0/3\n description client\n media-type rj45\n negotiation auto\n!\ninterface Vlan1\n ip address 10.0.0.110 255.255.255.0\n!\ninterface Vlan200\n ip address 10.0.200.110 255.255.255.0\n!\nip forward-protocol nd\n!\nno ip http server\nno ip http secure-server\n!\nip ssh version 2\nip scp server enable\n!\n!\n!\n!\n!\ncontrol-plane\n!\nbanner exec ^C\n**************************************************************************\n* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n* education. IOSv is provided as-is and is not supported by Cisco's      *\n* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n* of the IOSv Software or Documentation to any third party for any       *\n* purposes is expressly prohibited except as otherwise authorized by     *\n* Cisco in writing.                                                      *\n**************************************************************************^C\nbanner incoming ^C\n**************************************************************************\n* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n* education. IOSv is provided as-is and is not supported by Cisco's      *\n* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n* of the IOSv Software or Documentation to any third party for any       *\n* purposes is expressly prohibited except as otherwise authorized by     *\n* Cisco in writing.                                                      *\n**************************************************************************^C\nbanner login ^C\n**************************************************************************\n* IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n* education. IOSv is provided as-is and is not supported by Cisco's      *\n* Technical Advisory Center. Any use or disclosure, in whole or in part, *\n* of the IOSv Software or Documentation to any third party for any       *\n* purposes is expressly prohibited except as otherwise authorized by     *\n* Cisco in writing.                                                      *\n**************************************************************************^C\n!\nline con 0\nline aux 0\nline vty 0 4\n login local\nline vty 5 15\n login local\n!\nntp server pnpntpserver.ins.local\n!\nend",
    "candidate": "",
}


config_s1 = SelfTestData(
    name="s1",
    nornir_raw_result=nornir_raw_result_s1,
    test_data={"host": "S1", "startup_equals_running_config": True},
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
    params=[config_s1],
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
