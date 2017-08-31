interfacestatus
---------------

Check the interface status on a network device

.. literalinclude:: ../../../examples/interfacestatus.yml


Parameter
~~~~~~~~~

Interface: Interface name. Example `GigabitEthernet1`

Return
~~~~~~

Return true if the interface is up

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