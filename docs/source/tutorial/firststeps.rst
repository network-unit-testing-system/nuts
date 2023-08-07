First Steps with NUTS
=====================

This tutorial guides you through a minimal setup of the NetTowel Unit Testing System (NUTS, or nuts). A showcase is included in nuts' code that allows you to learn the basic mechanics of nuts without the need for an actual network -- find those details at the end of this tutorial.

Two major components are needed for nuts:

    #. A network inventory
    #. Test bundles

Here's an overview of how to organize your files so that NUTS can find everything it needs. The root folder also contains the virtual environment with the :doc:`nuts installation <../installation/install>`.
This example uses the Nornir SimpleInventory, but all inventory plugins are supported.

.. code:: shell

    .                       # NUTS root 
    ├── inventory           # your inventory
    │   └── hosts.yaml      # information on hosts
    ├── nr-config.yaml      # nornir configuration
    └── tests               # your test bundles
        └── test-definition-ping.yaml    

NOTE: If you already have an existing nornir configuration including an inventory you do not need to copy it into your NUTS test setup. Instead, you can directly refer to it `when executing the tests`__.

__ customInventory_

1. Network Inventory
--------------------

You must provide information on your network configuration so that nuts can interact with it. 
Currently, the implemented test cases in NUTS use `nornir <https://nornir.readthedocs.io/en/latest/>`__ and a config file ``nr-config.yaml`` (default) which provides the inventory.

A sample ``hosts.yaml`` (Nornir SampleInventory) might look like this:

.. code:: yaml

  R1:
    hostname: 10.0.0.42
    platform: ios
    username: Cisco
    password: cisco
    interfaces:
      - name: GigabitEthernet2
        ipv4_address: 172.16.0.42
      - name: Loopback0
        ipv4_address: 172.16.255.1
  R2:
    hostname: 10.20.0.24
    platform: ios
    username: Cisco
    password: cisco
    interfaces:
      - name: GigabitEthernet2
        ipv4_address: 172.16.0.24
      - name: Loopback0
        ipv4_address: 172.16.255.2

We provide the most basic example here with sample IP addresses and credentials. Please see `nornir's documentation <https://nornir.readthedocs.io/en/latest/tutorial/inventory.html>`__ on how to structure the inventory according to your needs. 

A sample ``nr-config.yaml`` might look like this:

.. code:: yaml

  inventory:
    plugin: SimpleInventory
    options:
      host_file: "inventory/hosts.yaml"
  runner:
    plugin: threaded
    options:
      num_workers: 100

If you set up the above folders and files, you are ready to write test bundles.

2. Test Bundle
--------------

A test bundle is a collection of tests that are logically related to each other, for example, tests that all revolve around "information on BGP neighbors". The test bundle describes which test definition should be collected and executed and provides data for those tests. The bundles are written as individual entries in a YAML file.

Currently, only YAML files are supported as test bundle format, but other data sources could be integrated with later versions of nuts. 

Structure of a Test Bundle
**************************

Each test bundle contains the following structure:

.. code:: yaml

  - test_module: <module that contains the test class> # optional
    test_class: <name of the test class>
    label: <label to uniquely identify the test> # optional 
    test_execution: <additional data used to execute the test> # optional
    test_data: <data used to generate the test instances>

``test_module``: Optional. The full path of the Python module that contains the test class to be used. This value is optional if the test class is registered in ``index.py`` of the pytest-nuts plugin. Note that it can be relevant in which directory ``pytest`` is started if local test modules are used. Using ``test_modules`` allows you to write your own test classes. **Note: We currently do not support self-written test modules, since upcoming refactorings might introduce breaking changes.**

``test_class``: Required. The name of the Python class which contains the tests that should be executed. Note that currently every test in this class is executed.

``label``: Optional. An additional identifier that can be used to distinguish between multiple occurrences of the same test class in a test bundle.

``test_execution``: Optional. Nuts uses nornir tasks to automatically interact with the network. This field contains additional information that is directly passed to the nornir task in the background. Therefore the key-value pairs must be consistent with the key-value pairs of the specific nornir task. 
As an example, the test definition ``TestNapalmPing`` calls a nornir task to execute napalm's ping-command. 
This allows the additional ``count`` parameter in ``test execution``, since it is in turn pre-defined by napalm. Please see the :doc:`chapter on test bundles <../testbundles/alltestbundles>` for more detailed explanations.

``test_data``: Required. Data that is used to parametrize the tests - basically what information each test instance needs. The structure of this section is specific to every test bundle, detailed in the chapter on :doc:`test bundles <../testbundles/alltestbundles>`. 

Since each test bundle looks a little different, please see the :doc:`chapter on test bundles <../testbundles/alltestbundles>` to see how each one is structured.

Sample Test-Bundle: Ping
************************

As an example, we now want to test if ``R1`` can ping ``R2``. Here's our sample test bundle:

.. code:: yaml

  - test_class: TestNapalmPing
    test_execution:
      count: 5
    test_data:
      - host: R1
        destination: 172.16.0.24
        expected: SUCCESS
        max_drop: 1

Notes: 

* ``test_execution:`` By using the pre-defined key-value pair ``count: 5``, we indicate that the ping should be executed 5 times.
* ``test_data.expected: SUCCESS``. The ping should be successful. The pre-defined values are either SUCCESS, FAIL, or FLAPPING.
* ``test_data.max_drop: 1``. Maximum one ping attempt is allowed to fail to still count as SUCCESS ping.


We save this file as ``test-definition-ping.yaml`` into the ``tests`` folder.


3. Running the Tests
--------------------

If everything is set up as shown above, run the test from the root folder:

.. code:: shell

    $ pytest tests/test-definition-ping.yaml

Pytest's output should then inform you if the test succeeded or not.

.. _customInventory:

Custom nornir configuration
***************************

If you already have a nornir configuration and inventory for your network you can reuse it by passing the parameter ``--nornir-config`` to the pytest command:

.. code:: shell

    $ pytest tests/test-definition-ping.yaml --nornir-config path/to/nr-config.yaml



4. Sample Test-Bundle Without a Network
---------------------------------------

The sample test bundle above requires a network inventory and a running network in the background. In case you want to learn how nuts works but do not have a network at hand, nuts comes with an offline showcase to display its functionality. Use it as follows:

#. Clone the `nuts repository <https://github.com/INSRapperswil/nuts>`__ and change into the cloned folder.
#. Create a `virtual environment (venv) <https://docs.python.org/3/library/venv.html>`__ in it and activate it.
#. Install nuts in the venv.
#. Run the showcase test bundle.

.. code:: shell

    $ git clone https://github.com/INSRapperswil/nuts && cd nuts
    $ python -m venv .venv && source .venv/bin/activate
    $ pip install .
    $ pytest tests/showcase_test/test-expanse.yaml

How it works: Each test module implements a context class to provide module-specific functionality to its tests. This context class is a  ``NutsContext`` or a subclass of it. This guarantees a consistent interface across all tests for test setup and execution. 

The predefined test classes which depend on a network all use `nornir <https://nornir.readthedocs.io/en/latest/>`__ in order to communicate with the network devices. Those test classes all derive from a more specific ``NornirNutsContext``, which provides a nornir instance and nornir-specific helpers. 

In order for the offline showcase to work, the test class derives from ``NutsContext`` and implements its own context class. See the code in ``nuts/tests/showcase/showcase_expanse.py`` to see the structure of this offline context class.



