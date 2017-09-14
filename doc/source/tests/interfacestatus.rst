interfacestatus
---------------

Check whether an interface is up.

.. literalinclude:: ../../../examples/interfacestatus.yml


Parameter
~~~~~~~~~

Interface: Interface name. Example `GigabitEthernet1`

Return
~~~~~~

``true`` if the interface is up, ``false`` otherwise.

.. code:: json

 {
     "result": true,
     "resulttype": "single"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Network devices with NAPALM

Requirements
~~~~~~~~~~~~

no special requirements
