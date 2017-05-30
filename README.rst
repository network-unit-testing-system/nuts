Nuts - Network Unit Testing System
##################################
Nuts is a network unit testing system, that automates tests in the network similar to unit tests you might know from programming.
The project uses saltstack and napalm for the communication with the network devices.
This project is currently under construction and we can't guarantee you that this code works.
If you have any question please reach out to https://github.com/HSRNetwork/Nuts or join https://networktocode.slack.com/

Installation of nuts
====================

The following Python versions are fully supported:

- Python 2.7


Pre-requirements
----------------
- Salt master
	Because nuts is fully based on saltstack you have to install and configure a salt master first.
	For the full installation guide please visit the `installation guide <https://docs.saltstack.com/en/latest/topics/installation/>`_. 
- Salt api
	To use nuts you also need salt-api which enables nuts to connect to the salt master over Http. For the installation guide visit `cherrypy documentation <https://docs.saltstack.com/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html/>`_.
- Napalm salt
	To create a connection from the salt master to your network device of choice there's a fantastic library called NAPALM which got an integration into saltstack. For the installation guide head to `napalm-salt repository <https://github.com/napalm-automation/napalm-salt/>`_.

Install on arch linux
---------------------
TODO

Install on ubuntu
-----------------
TODO

Install with pip
----------------

The recommended way to install nuts is using `pip <http://pip.readthedocs.org/en/latest/>`_:

::

    $ sudo pip install -U nuts

This will automatically install the latest version from the `Python Package
Index <https://pypi.python.org/pypi/nuts/>`__.

Manual Installation
-------------------
TODO UPDATE

Get code::

    $ git clone https://github.com/HSRNetwork/Nuts.git
    $ cd Nuts

Install::

    $ sudo python setup.py install

Usage
=======

usage: nuts.py [-h] [-v] [-m ITERATIONS] [-r RETRIES] [-c CONFIG] testfile

positional arguments:
  testfile                                  Start with a Testfile

optional arguments:
  -h, --help                                show this help message and exit
  -v, --validate                            Validates Testfile
  -m ITERATIONS, --iterations ITERATIONS    Changes the number of iterations that nuts waits for a result
  -r RETRIES, --retries RETRIES             Set the max retries for failed tests
  -c CONFIG, --config CONFIG                Config file formatted as YAML. Settings will be merged with ENVVARs

Testfiles
=========
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
 - connectivity         - checks the connectivity to a certain IP address with a simple ping. Takes the target IP address as a parameter
 - traceroute           - checks the connectivity to a certain IP address with a traceroute. Takes the target IP address as a parameter
 - interfacestatus      - checks if a specific interface is available. Takes the interface name as a parameter
 - interfacespeed       - checks the speed of a specific interface. Takes the interface name as a parameter
 - arp                  - checks the mac address of a specific IP address. Takes the IP address as a parameter
 - checkversion         - checks the version of the device. Takes no parameter
 - checkuser            - checks which users are available on the device. Takes no parameter

For more information about the availability visit `napalm docs <https://napalm.readthedocs.io/en/latest/support/index.html>`_.

The following commands are currently available for debian systems:
 - connectivity
 - traceroute
 - dnscheck
 - dhcpcheck
 - webresponse
 - portresponse

There are the following operators available:
 - =
 - <
 - >
 - not

Examples
========
There are a few more examples of test files available in the example folder. 

License
=======

The MIT License (MIT)

Copyright (c) 2016 Andreas Stalder, David Meister, Matthias Gabriel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
