connectivity
------------

Return result of the connectivity test.

.. literalinclude:: ../../../examples/connectivity.yml


Parameter
~~~~~~~~~

Destination: Domain name or ip address

Return
~~~~~~

True or False

Return True if the destination is reachable.

.. code:: json

 {
     "result": true,
     "resulttype": "single"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Network devices with NAPALM
- Debian family
- RadHat family

Requirements
~~~~~~~~~~~~

no special requirements