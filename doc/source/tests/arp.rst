arp
---

Checks the ARP entry for a given ip address

.. literalinclude:: ../../../examples/arp.yml


Parameter
~~~~~~~~~

Address: IP address for the arp lookup

Return
~~~~~~

Return the mac address stored in the arp table

.. code:: json

 {
     "result": 1000,
     "resulttype": "single"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Network devices with NAPALM

Requirements
~~~~~~~~~~~~

no special requirements