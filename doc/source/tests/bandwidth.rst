bandwidth
---------

Starts a iperf3 test to the destination and returns bits per second

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
- RadHat family

Requirements
~~~~~~~~~~~~

- iperf3