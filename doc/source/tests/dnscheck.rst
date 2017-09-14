dnscheck
--------

Checks if a domain is resolvable

.. literalinclude:: ../../../examples/dnscheck.yml


Parameter
~~~~~~~~~

Domain name: Domain to resolve

Return
~~~~~~

Return the list of responses. Supported query types are ``A``, ``AAAA``, ``MX``, ``NS``, ``SPF`` and ``TXT``.
As third option the domain server can be specified.

.. code:: json

 {
     "resulttype": "multiple",
     "result": [
         "192.30.253.113",
         "192.30.253.112"
     ]
 }

Supported platforms
~~~~~~~~~~~~~~~~~~~

- Debian family
- RedHat family

Requirements
~~~~~~~~~~~~

- nslookup

RedHat / Centos

.. code:: bash

    sudo yum install bind-utils
