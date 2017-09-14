traceroute
----------

Return the path of the traceroute

.. literalinclude:: ../../../examples/traceroute.yml


Parameter
~~~~~~~~~

Destination: Domain name or ip address

Return
~~~~~~

All responding hosts.

.. code:: json

 {
     "result": {
         "0": "172.16.17.2",
         "1": "10.10.10.1"
     },
     "resulttype": "multiple"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Network devices with NAPALM
- Debian family
- RedHat family

Requirements
~~~~~~~~~~~~

no special requirements
