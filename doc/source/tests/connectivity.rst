connectivity
------------

Performs a connectivity test.

.. literalinclude:: ../../../examples/connectivity.yml


Parameter
~~~~~~~~~

Destination: Domain name or ip address

Return
~~~~~~

``true`` if the destination is reachable, ``false`` otherwise.

.. code:: json

 {
     "result": true,
     "resulttype": "single"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Network devices with NAPALM
- Debian family
- RedHat family

Requirements
~~~~~~~~~~~~

no special requirements
