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

In order to parse answers from network devices, some NUTS test classes use `ntc-templates <https://github.com/networktocode/ntc-templates>`__ (TextFSM Templates for Network Devices). These tests rely on ntc-templates:

  * ``TestNetmikoCdpNeighbors``
  * ``TestNetmikoOspfNeighborsCount``
  * ``TestNetmikoOspfNeighbors``

If you run these test classes, please make sure to have ntc-templates installed in your project root - see `ntc-templates on Github <https://github.com/networktocode/ntc-templates>`__ for the installation instructions. The folder must lie on the same level as the test and the inventory folder.


Deinstallation
--------------

.. code:: shell
    
    pip uninstall nettowel-nuts


If you installed everything in a virtual environment, you can delete the folder that contains the virtual environment.
