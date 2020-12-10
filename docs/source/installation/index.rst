Installation of NUTS 
====================

Installation Instructions
-------------------------

NUTS is currently not published on the Python Package Index (`PyPI <https://pypi.org/>`_). It has to be cloned and installed manually.

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


Deinstallation
--------------

.. code:: shell
    
    pip uninstall nettowel-nuts


If you installed everything in a virtual environment, you can delete the folder that contains the virtual environment.
