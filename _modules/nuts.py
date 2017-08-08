# -*- coding: utf-8 -*-
'''
Nuts - Network Unit Testing System
===============

Unit testing system function, that automates tests in the network similar to unit tests.

:codeauthor: Urs Baumann <ubaumann@ins.hsr.ch>
:maturity:   new
:depends:    napalm
:platform:   unix

Dependencies
------------

- :mod:`napalm proxy minion <salt.proxy.napalm>`

.. versionadded:: TBD
.. versionchanged:: TBD
'''

from __future__ import absolute_import

import salt.client
import re
import json
import salt.config
from salt.client.ssh.client import SSHClient

client = SSHClient()
local = salt.client.LocalClient()
master = salt.client.Caller()

__virtualname__ = 'nuts'


def __virtual__():
    return __virtualname__


# ----------------------------------------------------------------------------------------------------------------------
# helper functions -- will not be exported
# ----------------------------------------------------------------------------------------------------------------------


def _returnMultiple(result):
    '''
    Wrap result with multiple result grid
    '''

    data = {}
    data['result'] = result
    data['resulttype'] = 'multiple'
    return data


def _returnSingle(result):
    '''
    Wrap result with single result grid
    '''

    data = {}
    data['result'] = result
    data['resulttype'] = 'single'
    return data


# ----------------------------------------------------------------------------------------------------------------------
# callable functions
# ----------------------------------------------------------------------------------------------------------------------


def connectivity(dest):
    '''
    Return result of the connectivity test.

    CLI Example:

    .. code-block:: bash

        salt '*' nuts.connectivity 10.10.10.1

    Example output:

    .. code-block:: python

        {
            "result": true,
            "resulttype": "single"
        }

    :param dest:
    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family in ['Debian', 'RedHat']:
        result = __salt__['cmd.run']('ping -c 3 {}'.format(dest))  # pylint: disable=undefined-variable
        text = bytes(result).decode(encoding='utf-8', errors='ignore')
        regex = '([0-9]*)% packet loss'
        r = re.compile(regex)
        m = r.search(text)
        return _returnSingle((int(float(m.group(1))) < 100))
    elif os_family == 'proxy':
        # at the moment there's a bug in the napalm-salt library which forces you to set all parameters fixed
        # https://github.com/saltstack/salt/pull/38577
        result = __salt__['net.ping'](dest, '', 255, 2, 100, 10)  # pylint: disable=undefined-variable
        # the absolute is needed because cisco returns -10 as packet_loss if they are not sent
        return _returnSingle(result['result'] and abs(result['out']['success']['packet_loss']) != 10)


def traceroute(dest):
    '''
    Return result of the traceroute test.

    CLI Example:

    .. code-block:: bash

        salt '*' nuts.traceroute 10.10.10.1

    Example output:

    .. code-block:: python

        {
            "result": {
                "0": "172.16.17.2",
                "1": "10.10.10.1"
            },
            "resulttype": "multiple"
        }


    :param dest:
    :return:
    '''

    json_data = {}
    resultList = []
    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family in ['Debian', 'RedHat']:
        result = __salt__['cmd.run']('traceroute {}'.format(dest))  # pylint: disable=undefined-variable
        text = bytes(result).decode(encoding='utf-8', errors='ignore')
        regex = '[0-9]*  ([0-9\.]*) \('
        for m in re.finditer(regex, text):
            resultList.append(m.group(1))
        json_data['result'] = resultList
        json_data['resulttype'] = 'multiple'
        return json.dumps(json_data)
    elif os_family == 'proxy':
        result = __salt__['net.traceroute'](dest)  # pylint: disable=undefined-variable
        if result['result']:
            probes = result['out']['success']
            hosts = {key: value['probes'][1]['host_name'] for key, value in probes.items()}
            return _returnMultiple(hosts)


def bandwidth(param):
    '''This function isn't working at the moment because it's not complient with the saltstack way'''
    '''
    if os == "linux":
        local.cmd(dst, 'cmd.run', ['iperf3 -s -D -1'])
        result = local.cmd(host, 'cmd.run', ['iperf3 -c ' + dst])
        text = bytes(result).decode(encoding="utf-8", errors='ignore')
        regex = "Bytes  ([0-9\.]*) ([a-zA-Z]bits\/sec)([\s]*receiver)"
        r = re.compile(regex)
        m = r.search(text)
        return  returnSingle(float(m.group(1)) * 1000.0 * 1000.0)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def dnscheck(param):
    '''
    Retruns if a domain is resolvable on the minion
    command `nslookup` is needed

    RedHat/Centos: sudo yum install bind-utils

    CLI Example:

    .. code-block:: bash

        salt "*" nuts.dnscheck google.ch

    Example output:

    .. code-block:: python

        {
            "result": true,
            "resulttype": "single"
        }

    :param param:
    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family in ['Debian', 'RedHat']:
        result = __salt__['cmd.run']('nslookup {}'.format(param))  # pylint: disable=undefined-variable
        text = bytes(result).decode(encoding='utf-8', errors='ignore')
        pattern = '(Name:[\s]*[a-z0-9.]*)'
        regex = re.compile(pattern)
        return _returnSingle(bool(re.search(regex, text)))


def dhcpcheck(dest):
    '''
    Pings the dhcp server and return True when a server response is recieved
    command `dhcping` is needed

    RedHat/Centos: sudo yum install bind-utils

    CLI Example:

    .. code-block:: bash

        salt "*" nuts.dhcpcheck 10.10.10.10

    Example output:

    .. code-block:: python

        {
            "result": true,
            "resulttype": "single"
        }

    :param dest:
    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family in ['Debian', 'RedHat']:
        result = __salt__['cmd.run']('dhcping -s {}'.format(dest))  # pylint: disable=undefined-variable
        text = bytes(result).decode(encoding='utf-8', errors='ignore')
        regex = '(Got answer)'
        return _returnSingle(bool(re.search(regex, text)))


def webresponse(dest, max_time=30):
    '''
    Returns True when the webserver response with `2__` or `3__`

    command `curl` needed

    .. code-block:: bash

        salt "*" nuts.webresponse http://github.com

    Example output:

    .. code-block:: python

        {
            "result": true,
            "resulttype": "single"
        }

    :param dest:
    :param max_time:
    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family in ['Debian', 'RedHat']:
        cmd = 'curl -Is {0} --max-time {1} | head -n 1'.format(dest, max_time)
        result = __salt__['cmd.run'](cmd)  # pylint: disable=undefined-variable
        text = bytes(result).decode(encoding='utf-8', errors='ignore')
        regex = '([23][0-9]{2} [OK|Created|Accepted|No|Moved|Found|Temporary])'
        return _returnSingle(bool(re.search(regex, text)))


def portresponse(dest, port):
    '''
    Returns all open ports from the given port range.

    command `nmap` needed

    .. code-block:: bash

        salt "*" nuts.portresponse 10.10.10.10 U:53,111,137,T:22-25,53,80,443,139,8080

    Example output:

    .. code-block:: python

        {
            "result": [
                "22/tcp",
                "53/tcp"
            ],
            "resulttype": "multiple"
        }

    :param dest:
    :param port:
    :return:
    '''

    result_list = []
    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family in ['Debian', 'RedHat']:
        result = __salt__['cmd.run']('nmap -p {0} {1}'.format(port, dest))  # pylint: disable=undefined-variable
        text = bytes(result).decode(encoding='utf-8', errors='ignore')
        pattern = '([0-9]*\/[a-z]*)[\s]*(open)'
        regex = re.compile(pattern, re.IGNORECASE)
        for m in regex.finditer(text):
            if m.group(2) == 'open':
                result_list.append(m.group(1))
        return _returnMultiple(result_list)


def checkuser():
    '''
    Returns a list of local users

    .. code-block:: bash

        salt "*" nuts.checkuser

    Example output:

    .. code-block:: python

        ????????????????????????????????????????????????

    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family == 'proxy':
        result = __salt__['users.config']()  # pylint: disable=undefined-variable
        if result['result']:
            return _returnMultiple(result['out'].keys())


def checkversion():
    '''


    .. code-block:: bash

        salt "*" nuts.checkversion

    Example output:

    .. code-block:: python

        {
            "result": "CSR1000V Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 15.5(2)S, RELEASE SOFTWARE (fc3)",
            "resulttype": "single"
        }

    :return:
    '''
    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family == 'proxy':
        result = __salt__['net.facts']()  # pylint: disable=undefined-variable
        if result['result']:
            if 'os_version' in result['out']:
                return _returnSingle(result['out']['os_version'])


def checkospfneighbors():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_ip_ospf_neighbor}"
        tree = getCiscoXML(str(dst), "", "sh ip ospf neighbor", "")
        for id in tree.iter(tag=namespace + 'NeighborID'):
            resultList.append(id.text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def countospfneighbors():
    '''
    value = checkospfneighbors(dst, os, user, pwd)
    json_data = json.loads(value[value.index('{'):(value.index('}') + 1)])
    return returnSingle(len(json_data["result"]))
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def checkospfneighborsstatus():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_ip_ospf_neighbor}"
        tree = getCiscoXML(dst, "", "sh ip ospf neighbor", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(id.find(namespace + 'NeighborID').text + ":" + id.find(namespace + 'State').text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def stpinterfacestate():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_interface_*}"
        tree = getCiscoXML(dst, param, "sh spanning-tree interface", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(id.find(namespace + 'Vlan').text + ":" + id.find(namespace + 'Sts').text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def stpinterfacerole():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_interface_*}"
        tree = getCiscoXML(dst, param, "sh spanning-tree interface", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(id.find(namespace + 'Vlan').text + ":" + id.find(namespace + 'Role').text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def stpinterfacecost():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_interface_*}"
        tree = getCiscoXML(dst, param, "sh spanning-tree interface", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(
                id.find(namespace + 'Vlan').text + ":" + id.find(namespace + 'Cost').text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def stprootid():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_root}"
        tree = getCiscoXML(dst, "", "sh spanning-tree root", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(
                id.find(namespace + 'Vlan').text + ":" + id.find(namespace + 'RootID').text.split(' ')[1])
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def stprootcost():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_root}"
        tree = getCiscoXML(dst, "", "sh spanning-tree root", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(
                id.find(namespace + 'Vlan').text + ":" + id.find(namespace + 'Cost').text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def stpvlaninterfaces():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_vlan_*}"
        tree = getCiscoXML(dst, "", "sh spanning-tree vlan", "")
        for id in tree.iter(tag=namespace + 'Interface'):
            resultList.append(id.text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def stpvlanblockedports():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_blockedports}"
        tree = getCiscoXML(dst, "", "sh spanning-tree blockedports", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(
                id.find(namespace + 'Name').text + ":" + id.find(namespace + 'BlockedInterfacesList').text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def vlanports():
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_vlan_id_*}"
        tree = getCiscoXML(dst, param, "sh vlan id", "")
        for id in tree.iter(tag=namespace + 'Ports'):
            resultList.append(id.text)
        return returnMultiple(resultList)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def interfacestatus(param):
    '''
    Returns True if the interface is up

    .. code-block:: bash

        salt "*" nuts.interfacestatus GigabitEthernet1

    Example output:

    .. code-block:: python

        {
            "result": true,
            "resulttype": "single"
        }

    :param param:
    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family == "proxy":
        result = __salt__['net.interfaces']()  # pylint: disable=undefined-variable
        if result['result']:
            if param in result['out']:
                return _returnSingle(result['out'][param]['is_up'])


def interfacevlan():
    '''
    result = ""
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_interface_*_status}"
        tree = getCiscoXML(dst, param, "sh interface", " status")
        for id in tree.iter(tag=namespace + 'Vlan'):
            result = (id.text)
        return returnSingle(result)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def interfaceduplex():
    '''
    result = ""
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_interface_*_status}"
        tree = getCiscoXML(dst, param, "sh interface", " status")
        for id in tree.iter(tag=namespace + 'Duplex'):
            result = id.text
        return returnSingle(result)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def interfacespeed(param):
    '''
    Returns the interface speed

    .. code-block:: bash

        salt "*" nuts.interfacespeed GigabitEthernet1

    Example output:

    .. code-block:: python

        {
            "result": 1000,
            "resulttype": "single"
        }

    :param param:
    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family == "proxy":
        result = __salt__['net.interfaces']()  # pylint: disable=undefined-variable
        if result['result']:
            if param in result['out']:
                return _returnSingle(result['out'][param]['speed'])


def cdpneighbor():
    '''
    result = ""
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_cdp_neighbors_*}"
        tree = getCiscoXML(dst, param, "sh cdp neighbors", "")
        for id in tree.iter(tag=namespace + 'DeviceID'):
            result = id.text
        return returnSingle(result)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def cdpneighborcount():
    '''
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_cdp_neighbors}"
        tree = getCiscoXML(dst, "", "sh cdp neighbors", "")
        i = 0
        for id in tree.iter(tag=namespace + 'entry'):
            i += 1
        return returnSingle(i)
    '''
    raise NotImplementedError('This function isn\'t implemented right now')


def arp(param):
    '''


    .. code-block:: bash

        salt "*" nuts.arp 10.10.10.10

    Example output:

    .. code-block:: python

        {
            "result": "00:00:0C:9F:F1:35",
            "resulttype": "single"
        }

    :param param:
    :return:
    '''

    os_family = __grains__['os_family']  # pylint: disable=undefined-variable
    if os_family == 'proxy':
        result = __salt__['net.arp']('', param)  # pylint: disable=undefined-variable
        if result['result']:
            for entry in result['out']:
                if entry['ip'] == param:
                    return _returnSingle(entry['mac'])
