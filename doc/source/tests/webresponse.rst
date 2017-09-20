webresponse
-----------

Checks the HTTP status code of a webserver

.. literalinclude:: ../../../examples/webresponse.yml


Parameter
~~~~~~~~~

Web Server: IP address or url

Return
~~~~~~

``true`` if the HTTP status code is in the ``2xx`` or ``3xx`` range, ``false`` otherwise.

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

- curl
