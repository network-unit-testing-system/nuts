Test Commands
=============

Testfiles
---------
The structure of the testfile has to be compliant with the testschema found in ``nuts/src/service/testSchema.yaml``.
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

Please note that device attributes get passed directly to the salt master which determines the targeted minions using *globbing*.
For more information about globbing head to `saltstack globbing <https://docs.saltstack.com/en/latest/topics/targeting/globbing.html#globbing>`_.
If multiple minions are targeted each of them has to satisfy the expected value for the test to pass.

This way you can run a test on all test nodes with one statement.

.. code:: yaml

 devices: testnode*


Supported commands
------------------

Network devices
~~~~~~~~~~~~~~~

The following commands are currently available via ``napalm-salt``.

- **connectivity**         - checks the connectivity to a certain IP address with a simple ping. Takes the target IP address as a parameter
- **traceroute**           - checks the connectivity to a certain IP address with a traceroute. Takes the target IP address as a parameter
- **interfacestatus**      - checks if a specific interface is available. Takes the interface name as a parameter
- **interfacespeed**       - checks the speed of a specific interface. Takes the interface name as a parameter
- **arp**                  - checks the mac address of a specific IP address. Takes the IP address as a parameter
- **checkversion**         - checks the version of the device. Takes no parameter
- **checkuser**            - checks which users are available on the device. Takes no parameter

For more information about the availability of napalm commands, visit `napalm docs <https://napalm.readthedocs.io/en/latest/support/index.html>`_.


Linux devices
~~~~~~~~~~~~~

The following commands are currently available for Debian/RedHat systems:

- **connectivity**
- **traceroute**
- **dnscheck**
- **dhcpcheck**
- **webresponse**
- **portresponse**
- **bandwidth**

Supported operators
~~~~~~~~~~~~~~~~~~~

The following operators are available:

- ``=``
- ``<``
- ``>``
- ``not``


Setup & Teardown
----------------

To prepare and clean up a test, Nuts supports setup and teardown tasks. It works quit similar to the python
unit testing functions. As an additional feature, It is possible to save the return value to use it with later commands.
Saved data is only available in the same test scope.

In the following example, the command in the setup section returns a list of IP addresses. This list is saved in the
variable named ``ip``. In the parameter list we use jinja2 syntax to get the first IP address. The test is passed when
``srvlnx0001`` can ping the first IP address of ``srvlnx0099``.

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

With globbing, when multiple minions are respondig to a command with the ``save`` keyword, a dict with the minion name as the key will be created.

As commands you can use all the SaltStack `Execution Modules <https://docs.saltstack.com/en/latest/ref/modules/all/index.html>`_
your Salt environment is supporting. Commands that do not contain a point ``.`` will have ``nuts.`` prepended automatically.


Synchronous or asynchronous
---------------------------

Nuts first executes all asynchronous test. After finishing, synchronous task are then executed sequentially.
Per default all test which have neither setup nor teardown task are asynchronous, while all other test are synchronous.
You can override the default behavior with the ``async`` keyword in the test definition.

.. code:: yaml

 async: False


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
