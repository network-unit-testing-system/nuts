Installation of NUTS 
====================

Installation Instructions
-------------------------

Nuts requires Python 3.9 or higher.

Installation via pip
....................

NUTS is published on the Python Package Index (`PyPI <https://pypi.org/>`_), therefore you can install nuts using ``pip``:

.. code:: shell

    pip install nuts

Installation via poetry
.......................

Nuts uses `poetry <https://python-poetry.org/>`__ as a dependency manager.

#. `Install poetry <https://python-poetry.org/docs/#installation>`__.
#. Clone the `nuts repository <https://github.com/INSRapperswil/Nuts.git>`__
#. Change into the cloned folder, then install all necessary dependencies: ``$ poetry install``
#. Install nuts: ``$ pip install .``

Installation via container
..........................

Nuts is also available in a dockerized version. It uses the GitHub registry.

.. code:: shell

    docker pull ghcr.io/network-unit-testing-system/nuts:latest
    docker run -it ghcr.io/network-unit-testing-system/nuts


Bootstrap NUTS
----------------
After installing NUTS, you can bootstrap the project. ``nuts-init`` will create the necessary folder structure and files.

.. code:: shell

    nuts-init


Parsing with ntc-templates
--------------------------

In order to parse answers from network devices, some NUTS test classes use `netmiko in combination with ntc-templates <https://ktbyers.github.io/netmiko/#textfsm-integration>`__ (ntc-templates: TextFSM Templates for Network Devices). These NUTS tests rely on ntc-templates:

  * ``TestNetmikoCdpNeighbors``
  * ``TestNetmikoOspfNeighborsCount``
  * ``TestNetmikoOspfNeighbors``

If you run these test classes, please make sure to configure access to ntc-templates correctly:

  1. Clone the `ntc-templates repository <https://github.com/networktocode/ntc-templates.git>`__ into your project root, on the same hierarchical level as your ``inventory`` and ``tests`` folder.
  2. Set environment variable: 

.. code:: shell

  $ export NET_TEXTFSM=/path/to/ntc-templates/templates/

`More on Netmiko and TextFSM <https://pynet.twb-tech.com/blog/automation/netmiko-textfsm.html>`__


Uninstallation
--------------

.. code:: shell
    
    pip uninstall nuts


If you installed everything in a virtual environment, you can delete the folder that contains the virtual environment.
