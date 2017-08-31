portresponse
------------

Checks for open ports

.. literalinclude:: ../../../examples/portresponse.yml


Parameter
~~~~~~~~~

Destination: Domain name or ip address

Ports: Number or ranges. Use `U:53` for a udp port and `T:22` for tcp port. Example: `U:53,111,137,T:22-25,53,80,443,139,8080`

Return
~~~~~~

Return all open ports on the destination host

.. code:: json

 {
     "result": [
         "22/tcp",
         "53/tcp"
     ],
     "resulttype": "multiple"
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Debian family
- RadHat family

Requirements
~~~~~~~~~~~~

- nmap