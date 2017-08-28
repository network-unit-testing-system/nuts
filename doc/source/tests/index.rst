Test Commands
=============

Testfiles
---------
The structure of the testfile has to be compliant with the testschema found in the folder nuts/src/service/testSchema.yaml.
An example could be:

.. code:: yaml

 - name: example_arp
   command: arp
   devices: cisco.csr.1000v
   parameter: [192.168.16.128]
   operator: '='
   expected: '00:0C:29:EA:D1:68'

Please note that the devices attribute gets directly passed to the salt master which determines the targeted minions with so called globbing. For more information what's globbing head to `saltstack globbing <https://docs.saltstack.com/en/latest/topics/targeting/globbing.html#globbing>`_.
If multiple minions are targeted each of them has to satisify the expected value for the test to pass.

The following commands are currently available with napalm-salt if this command is available on your device is also dependent on the availability of der underlying functions of napalm:

- **connectivity**         - checks the connectivity to a certain IP address with a simple ping. Takes the target IP address as a parameter
- **traceroute**           - checks the connectivity to a certain IP address with a traceroute. Takes the target IP address as a parameter
- **interfacestatus**      - checks if a specific interface is available. Takes the interface name as a parameter
- **interfacespeed**      - checks the speed of a specific interface. Takes the interface name as a parameter
- **arp**                  - checks the mac address of a specific IP address. Takes the IP address as a parameter
- **checkversion**         - checks the version of the device. Takes no parameter
- **checkuser**            - checks which users are available on the device. Takes no parameter

For more information about the availability visit `napalm docs <https://napalm.readthedocs.io/en/latest/support/index.html>`_.

The following commands are currently available for debian systems:

- **connectivity**
- **traceroute**
- **dnscheck**
- **dhcpcheck**
- **webresponse**
- **portresponse**

There are the following operators available:

- =
- <
- >
- not


Details:

.. toctree::
   :maxdepth: 1

   connectivity
   traceroute
   interfacestatus
   interfacespeed
   arp
   checkversion
   checkuser
   dnscheck
   dhcpcheck
   webresponse
   portresponse
   bandwidth