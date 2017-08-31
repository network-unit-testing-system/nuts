dnscheck
--------

Checks if a domain is resolvable

.. literalinclude:: ../../../examples/dnscheck.yml


Parameter
~~~~~~~~~

Domain to resolve: Domain name

Return
~~~~~~

True or False

Return True if the domain is resolvable

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

- nslookup

RedHat / Centos

.. code:: bash

    sudo yum install bind-utils