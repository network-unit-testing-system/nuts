dhcpcheck
---------

Checks if the dhcp server is responding

.. literalinclude:: ../../../examples/dhcpcheck.yml


Parameter
~~~~~~~~~

DHCP Server: IP address

Return
~~~~~~

True or False

Return True if the dhcp server is response

.. code:: json

 {
     "result": true,
     "resulttype": "single"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Debian family
- RadHat family

Requirements
~~~~~~~~~~~~

- dhcping