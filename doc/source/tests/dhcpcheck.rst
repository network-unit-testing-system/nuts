dhcpcheck
---------

Checks if a DHCP server is responding

.. literalinclude:: ../../../examples/dhcpcheck.yml


Parameter
~~~~~~~~~

DHCP Server: IP address

Return
~~~~~~

``true`` if the DHCP server is responding, ``false`` otherwise.

.. code:: json

 {
     "result": true,
     "resulttype": "single"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Debian family
- RedHat family

Requirements
~~~~~~~~~~~~

- dhcping
