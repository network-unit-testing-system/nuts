Installation of NUTS 
====================

Installation Instructions
-------------------------

NUTS is currently not published via pip. It has to be cloned and installed manually.

.. todo::
    
    Use public repository to access code and retest the installation instructions.

.. code:: shell

   git clone <public repository>

   cd nettowel-nuts

   # create virtual environment
   python -m venv .venv

   # activate virtual environment
   source .venv/bin/activate

   # install NUTS
   pip install <your_nuts_directory>

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


Deinstallation
--------------

.. code:: shell
    
    pip uninstall nettowel-nuts


If you installed everything in a virtual environment, you can delete the folder that contains the virtual environment.
