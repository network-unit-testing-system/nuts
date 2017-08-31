webresponse
-----------

Checks the response code of a webserver

.. literalinclude:: ../../../examples/webresponse.yml


Parameter
~~~~~~~~~

DHCP Server: IP address

Return
~~~~~~

True or False

Return True if the http response code is in the 200 or 300 range

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

- curl