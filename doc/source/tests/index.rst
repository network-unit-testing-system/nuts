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

Device targeting
----------------

Please note that the devices attribute gets directly passed to the salt master which determines the targeted minions with so called globbing.
For more information what's globbing head to `saltstack globbing <https://docs.saltstack.com/en/latest/topics/targeting/globbing.html#globbing>`_.
If multiple minions are targeted each of them has to satisfy the expected value for the test to pass.

So you can run a test on all test nodes with one statement

.. code:: yaml

 devices: testnode*


Supported commands
------------------

Network devices
~~~~~~~~~~~~~~~

The following commands are currently available with napalm-salt if this command is available on your device is also dependent on the availability of der underlying functions of napalm:

- **connectivity**         - checks the connectivity to a certain IP address with a simple ping. Takes the target IP address as a parameter
- **traceroute**           - checks the connectivity to a certain IP address with a traceroute. Takes the target IP address as a parameter
- **interfacestatus**      - checks if a specific interface is available. Takes the interface name as a parameter
- **interfacespeed**       - checks the speed of a specific interface. Takes the interface name as a parameter
- **arp**                  - checks the mac address of a specific IP address. Takes the IP address as a parameter
- **checkversion**         - checks the version of the device. Takes no parameter
- **checkuser**            - checks which users are available on the device. Takes no parameter

For more information about the availability visit `napalm docs <https://napalm.readthedocs.io/en/latest/support/index.html>`_.


Linux devices
~~~~~~~~~~~~~

The following commands are currently available for debian/redhat systems:

- **connectivity**
- **traceroute**
- **dnscheck**
- **dhcpcheck**
- **webresponse**
- **portresponse**

Supported operators
~~~~~~~~~~~~~~~~~~~

There are the following operators available:

- =
- <
- >
- not

Synchronous or asynchronous
---------------------------

Nuts starts first all asynchronous test and after finishing, the synchronous task are started sequentially.
Per default all test without any setup or teardown task are asynchronous and the test with a setup or teardown task are synchronous.
You can override the default with the keyword `async` in the test definition.

.. code:: yaml

 async: False



Setup & Teardown
----------------

To prepare and clean up the test, Nuts have the setup and teardown capabilities. It works quit similar to the python
unit testing functions. As an additional feature, It is possible to save the return value to use it on a later command.
Saved data are only in the same test scope available.

In the following example, the command in the setup section returns a list of ip addresses. This list is saved with the
variable name `ip`. On the parameter list we use jinja2 syntax to get the first ip address. The test is passed when
`srvlnx0001` can ping the first ip address of `srvlnx0099`.

.. code:: yaml

 - name: ping_srvlnx0099
   command: bandwidth
   devices: srvlnx0001
   parameter: ['{{ ip[0] }}']
   operator: '='
   expected: True
   setup:
   - command: network.ip_addrs
     devices: srvlnx0099
     save: ip

When using globbing and multiple minions are responding to as saved marked command, a dictionary with the minion name as key will be created.

As commands you can use all the SaltStack `Execution Modules <https://docs.saltstack.com/en/latest/ref/modules/all/index.html>`_
the installed Salt environment is supporting.


Command details
---------------

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