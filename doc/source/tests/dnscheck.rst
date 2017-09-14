dnscheck
--------

Checks if a domain is resolvable

.. literalinclude:: ../../../examples/dnscheck.yml


Parameter
~~~~~~~~~

Domain name: Domain to resolve

Return
~~~~~~

``true`` if the domain is resolveable, ``false`` otherwise.

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

- nslookup

RedHat / Centos

.. code:: bash

    sudo yum install bind-utils
