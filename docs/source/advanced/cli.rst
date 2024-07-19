Advanced Options
================

Nuts can be tweaked if the default options are not sufficient.

Custom Nornir Inventory
-----------------------

If you already have a nornir configuration and inventory for your network you can reuse it by passing the parameter ``--nornir-config`` to the pytest command:

.. code:: shell

    $ pytest tests/test-definition-ping.yaml --nornir-config path/to/nr-config.yaml


It will default back to the local directory.


Disable caching of the Nornir Inventory
---------------------------------------

For performance reasons the Nornir Inventory will be internally cached. If you wish to disable this behavior pass the parameter ``--nornir-cache-disable`` to the pytest command:

.. code:: shell

    $ pytest tests/test-definition-ping.yaml --nornir-cache-disable


