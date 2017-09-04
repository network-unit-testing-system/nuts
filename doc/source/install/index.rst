Installation
============

Nuts is a python tool and the installation is pretty easy. For the communication with the Salt master the API is used.
So there is no need for root permissions on the system. In the sub pages you will find additional help to the integration

.. toctree::
   :maxdepth: 1

   salt_setup
   salt_api
   salt_napalm

Python version
--------------

The following Python versions are fully supported:

- Python 2.7
- Python 3.6


Install with pip
----------------

The recommended way to install nuts is using `pip <http://pip.readthedocs.org/en/latest/>`_:

.. code-block:: bash

    $ sudo pip install -U nuts

This will automatically install the latest version from the `Python Package
Index <https://pypi.python.org/pypi/nuts/>`__.

Manual Installation
-------------------
.. TODO UPDATE

.. code-block:: bash

    $ git clone https://github.com/HSRNetwork/Nuts.git
    $ cd Nuts

.. code-block:: bash

    $ sudo python setup.py install

Custom SaltStack Execution Module
---------------------------------

Nuts uses a custom salt execution module to get the test data. It's is located in the folder ``_modules``.
If the ``file_roots`` is not changed, copy the file to ``/srv/salt/_modules`` on your salt master and sync the modules.
More details and links are in the :doc:`SaltStack Setup<salt_setup>` section.

.. code-block:: bash

    cp _modules/nuts.py /srv/salt/_modules/
    salt \* saltutil.sync_modules

Usage
-----

usage: nuts.py [-h] [-v] [-m ITERATIONS] [-r RETRIES] [-c CONFIG] testfile

positional arguments:
  testfile                                  Start with a Testfile

optional arguments:
  -h, --help                                show this help message and exit
  -v, --validate                            Validates Testfile
  -m ITERATIONS, --iterations ITERATIONS    Changes the number of iterations that nuts waits for a result
  -r RETRIES, --retries RETRIES             Set the max retries for failed tests
  -c CONFIG, --config CONFIG                Config file formatted as YAML. Settings will be merged with ENVVARs

Configuration
-------------
You can use a YAML formatted configuration file and/or set environment variables
Configuration options:

- NUTS_SALT_REST_API_URL
- NUTS_SALT_REST_API_USERNAME
- NUTS_SALT_REST_API_PASSWORD
- NUTS_SALT_REST_API_EAUTN
- NUTS_MAX_RETRIES
- NUTS_WAIT_ITERATIONS
- NUTS_LOG_FILE_LEVEL
- NUTS_LOG_CONSOLE_LEVEL
- NUTS_LOG_FOLDER


config.yml example:

.. code:: yaml

 NUTS_SALT_REST_API_URL: 'http://salt-master.lab:8000'
 NUTS_SALT_REST_API_USERNAME: 'myUser'
 NUTS_SALT_REST_API_PASSWORD: 'myPassword'
 NUTS_SALT_REST_API_EAUTH: 'pam'
