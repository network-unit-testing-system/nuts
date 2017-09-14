bandwidth
---------

Starts an ``iperf3`` test to the destination and returns the bandwith in bit/second.

.. literalinclude:: ../../../examples/bandwidth.yml


Parameter
~~~~~~~~~

Destination: Domain name or ip address of the iperf3 server

Return
~~~~~~

Returns bits per second

.. code:: json

 {
     "result": 939010154.975192,
     "resulttype": "single"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Debian family
- RedHat family

Requirements
~~~~~~~~~~~~

- iperf3
