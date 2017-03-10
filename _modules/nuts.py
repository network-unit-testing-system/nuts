import salt.client
import re
import json
import salt.config
import xml.etree.ElementTree as ET
from salt.client.ssh.client import SSHClient

client = SSHClient()
local = salt.client.LocalClient()
master = salt.client.Caller()

__virtualname__ = 'nuts'


def __virtual__():
    return __virtualname__


def getCiscoXML(dst, param, cmd, attribut):
    value = master.cmd('cmd.run', "salt-ssh " + str(dst) + " -i -r '" + str(cmd) + " " + str(
        param) + " " + str(attribut) + " | format flash:nuts.odm' --roster-file=/etc/salt/roster")
    xml = value[value.index('<'):len(value)]
    return ET.fromstring(xml)


def returnMultiple(result):
    json_data = {}
    json_data["result"] = result
    json_data["resulttype"] = "multiple"
    return json.dumps(json_data)


def returnSingle(result):
    json_data = {}
    json_data["result"] = result
    json_data["resulttype"] = "single"
    return json.dumps(json_data)


def connectivity(param):
    os = __grains__['os_family']
    if os == "Debian":
        result = __salt__['cmd.run']('ping -c 3 {}'.format(param))
        text = bytes(result).decode(encoding="utf-8", errors='ignore')
        regex = "([0-9]*)% packet loss"
        r = re.compile(regex)
        m = r.search(text)
        return returnSingle((int(float(m.group(1))) < 100))
    elif os == "proxy":
        #at the moment there's a bug in the napalm-salt library which forces you to set all parameters fixed 
        #https://github.com/saltstack/salt/pull/38577
        result = __salt__['net.ping'](param,'',255,2,100,10)
        #the absolute is needed because cisco returns -10 as packet_loss if they are not sent
        return returnSingle(result['result'] and abs(result['out']['success']['packet_loss']) != 10)
       
def traceroute(param):
    json_data = {}
    resultList = []
    os = __grains__['os_family']
    if os == "Debian":
        result = __salt__['cmd.run']('traceroute {}'.format(param))
        text = bytes(result).decode(encoding="utf-8", errors='ignore')
        regex = "[0-9]*  ([0-9\.]*) \("
        for m in re.finditer(regex, text):
            resultList.append(m.group(1))
        json_data["result"] = resultList
        json_data["resulttype"] = "multiple"
        return json.dumps(json_data)
    elif os == "proxy":
        result = __salt__['net.traceroute'](param)
        if result['result']:
            probes = result['out']['success']
            hosts = {key: value['probes'][1]['host_name'] for key, value in probes.items()}
            return returnMultiple(hosts)


def bandwidth(dst, host, os, user, pwd):
    '''This function isn't working at the moment because it's not complient with the saltstack way'''
    raise NotImplementedError('This function isn\'t implemented right now')
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

def dnscheck(param):
    os = __grains__['os_family']
    if os == "Debian":
        result = __salt__['cmd.run']('nslookup {}'.format(param))
        text = bytes(result).decode(encoding="utf-8", errors='ignore')
        regex = "(Name:[\s]*[a-z0-9.]*)"
        r = re.compile(regex)
        return returnSingle(bool(re.search(regex, text)))


def dhcpcheck(param):
    os = __grains__['os_family']
    if os == "Debian":
        result = __salt__['cmd.run']('dhcping -s {}'.format(param))
        text = bytes(result).decode(encoding="utf-8", errors='ignore')
        regex = "(Got answer)"
        r = re.compile(regex)
        return returnSingle(bool(re.search(regex, text)))


def webresponse(param):
    os = __grains__['os_family']
    if os == "Debian":
        result = __salt__['cmd.run']('curl -Is {} | head -n 1'.format(param))
        text = bytes(result).decode(encoding="utf-8", errors='ignore')
        regex = "([0-9]{3} OK)"
        r = re.compile(regex)
        return returnSingle(bool(re.search(regex, text)))


def portresponse(param,port):
    resultList = []
    os = __grains__['os_family']
    if os == "Debian":
        result = __salt__['cmd.run']('nmap -p {} {}'.format(port,param))
        text = bytes(result).decode(encoding="utf-8", errors='ignore')
        regex = "([0-9]*)\/[a-z]* (open)"
        for m in re.finditer(regex, text):
            if m.group(2) == "open":
                resultList.append(m.group(1))
        return returnMultiple(resultList)


def checkuser():
    resultList = []
    os = __grains__['os_family']
    if os == "proxy":
        result = __salt__['users.config']()
        if result['result']:
            return returnMultiple(result['out'].keys())
    

def checkversion():
    os = __grains__['os_family']
    if os == "proxy":
        result = __salt__['net.facts']()
        if result['result']:
            if 'os_version' in result['out']:
                return returnSingle(result['out']['os_version'])
    
    
def checkospfneighbors(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_ip_ospf_neighbor}"
        tree = getCiscoXML(str(dst), "", "sh ip ospf neighbor", "")
        for id in tree.iter(tag=namespace + 'NeighborID'):
            resultList.append(id.text)
        return returnMultiple(resultList)
    '''

def countospfneighbors(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    value = checkospfneighbors(dst, os, user, pwd)
    json_data = json.loads(value[value.index('{'):(value.index('}') + 1)])
    return returnSingle(len(json_data["result"]))
    '''

def checkospfneighborsstatus(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_ip_ospf_neighbor}"
        tree = getCiscoXML(dst, "", "sh ip ospf neighbor", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(id.find(namespace + 'NeighborID').text + ":" + id.find(namespace + 'State').text)
        return returnMultiple(resultList)
    '''

def stpinterfacestate(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_interface_*}"
        tree = getCiscoXML(dst, param, "sh spanning-tree interface", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(id.find(namespace + 'Vlan').text + ":" + id.find(namespace + 'Sts').text)
        return returnMultiple(resultList)
    '''

def stpinterfacerole(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_interface_*}"
        tree = getCiscoXML(dst, param, "sh spanning-tree interface", "")
        for id in tree.iter(tag=namespace + 'entry'):
            resultList.append(id.find(namespace + 'Vlan').text + ":" + id.find(namespace + 'Role').text)
        return returnMultiple(resultList)
    '''

def stpinterfacecost(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
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

def stprootid(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
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

def stprootcost(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
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

def stpvlaninterfaces(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_spanning-tree_vlan_*}"
        tree = getCiscoXML(dst, "", "sh spanning-tree vlan", "")
        for id in tree.iter(tag=namespace + 'Interface'):
            resultList.append(id.text)
        return returnMultiple(resultList)
    '''

def stpvlanblockedports(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
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

def vlanports(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    resultList = []
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_vlan_id_*}"
        tree = getCiscoXML(dst, param, "sh vlan id", "")
        for id in tree.iter(tag=namespace + 'Ports'):
            resultList.append(id.text)
        return returnMultiple(resultList)
    '''

def interfacestatus(param):
    os = __grains__['os_family']
    if os == "proxy":
        result = __salt__['net.interfaces']()
        if result['result']:
            if param in result['out']:
                return returnSingle(result['out'][param]['is_up'])

def interfacevlan(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    result = ""
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_interface_*_status}"
        tree = getCiscoXML(dst, param, "sh interface", " status")
        for id in tree.iter(tag=namespace + 'Vlan'):
            result = (id.text)
        return returnSingle(result)
    '''

def interfaceduplex(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    result = ""
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_interface_*_status}"
        tree = getCiscoXML(dst, param, "sh interface", " status")
        for id in tree.iter(tag=namespace + 'Duplex'):
            result = id.text
        return returnSingle(result)
    '''

def interfacespeed(param):
    os = __grains__['os_family']
    if os == "proxy":
        result = __salt__['net.interfaces']()
        if result['result']:
            if param in result['out']:
                return returnSingle(result['out'][param]['speed'])


def cdpneighbor(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    result = ""
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_cdp_neighbors_*}"
        tree = getCiscoXML(dst, param, "sh cdp neighbors", "")
        for id in tree.iter(tag=namespace + 'DeviceID'):
            result = id.text
        return returnSingle(result)
    '''

def cdpneighborcount(dst, param, os, user, pwd):
    raise NotImplementedError('This function isn\'t implemented right now')
    '''
    if os == 'ios':
        namespace = "{ODM://flash:nuts.odm//show_cdp_neighbors}"
        tree = getCiscoXML(dst, "", "sh cdp neighbors", "")
        i = 0
        for id in tree.iter(tag=namespace + 'entry'):
            i += 1
        return returnSingle(i)
    '''

def arp(param):
    os = __grains__['os_family']
    if os == "proxy":
        result = __salt__['net.arp']('',param)
        if result['result']:
            for entry in result['out']:
                if(entry['ip'] == param):
                    return returnSingle(entry['mac'])