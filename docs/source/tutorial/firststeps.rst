First Steps with NUTS
=====================

This short tutorial guides you through a minimal setup to use NUTS.

Two major components are needed for NUTS:

    #. A network inventory
    #. Test bundles

1. Network Inventory
--------------------

You must provide information on your network configuration so that NUTS can actually interact with it. Currently, NUTS uses a `nornir inventory <https://nornir.readthedocs.io/en/latest/tutorial/inventory.html>`__ as network configuration and ``nr-config.yaml`` which uses that inventory.

Here's a sample overview on how to organise files so that NUTS can find everything it needs. The root folder also contains also the virtual environment in with the :doc:`NUTS installation <../installation/index>`.

.. code:: shell

    .                       # NUTS root 
    ├── inventory           # your inventory
    │   └── hosts.yaml
    ├── nr-config.yaml      # nornir configuration
    └── tests               # your test bundles
        └── test-definition-ping.yaml

A sample ``hosts.yaml`` might look like this:

.. code:: shell

  ---
  R1:
    hostname: 10.0.0.42
    platform: ios
    username: Cisco
    password: cisco
    data:
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
    data:
      interfaces:
        - name: GigabitEthernet2
          ipv4_address: 172.16.0.24
        - name: Loopback0
          ipv4_address: 172.16.255.2

We provide the most basic exmaple here. Please see `nornir's documentation <https://nornir.readthedocs.io/en/latest/tutorial/inventory.html>`__ on how you can structure the inventory according to your needs. 

A sample ``nr-config.yaml`` might look like this:

.. code:: yaml

  ---
  inventory:
  plugin: SimpleInventory
  options:
      host_file: "inventory/hosts.yaml"
  runner:
  plugin: threaded
  options:
      num_workers: 100

If you set up the above folders and files, you're read to write test bundles.

2. Test Bundle
--------------

A test bundle is a YAML-file that is parsed by NUTS. It describes which test definitions should be collected and executed and provides data for those tests. Such a test bundle contains information on how to run a specific test, such das "ping hosts" or "retrieve information of BGP neighbors".

Currently only YAML files are supported as test bundle format, but other sources such as other file formats or database entries can be considered in later NUTS versions.

Structure of a Test Bundle
**************************

Each test bundle contains the following structure:

.. code:: yaml

    ---
    - test_module: <module that contains the test class> # optional
      test_class: <name of the test class>
      label: <label to uniquely identify the test> # optional 
      test_execution: <additional data used to execute the test> # optional
      test_data: <data used to generate the test cases>

``test_module``: Optional. The full path of the python module that contains the test class to be used. This value is optional if the test class is registered in index.py of the pytest-nuts plugin. Note that it can be relevant in which directory ``pytest`` is started if local test modules are used.

``test_class``: Required. The name of the python class which contains the tests that should be executed.Note that currently every test in this class will be executed.

``label``: Optional. Additional identifier that can be used to distinguish between multiple occurrences of the same 
test class in a test bundle.

``test_execution``: Optional. NUTS uses nornir tasks to automatically interact with the network. This field contains additional information that is directly passed to the nornir task in the background. Therefore the key-value pairs must be consistent with the key-value pairs of the specific nornir task. 
As an example, the test definition ``napalm_ping.py`` calls a nornir task to execute napalm's ping-command. 
This allows the additional ``max_drop`` parameter in ``test execution``, since it is in turn pre-defined by napalm. Please see the test bundles for links to the specific extra commands.

``test_data``: Required. Data that is used to parametrize the tests - basically what information your actual test needs. The structure of this section is specific to every test bundle.

Since each test bundle looks a little different, please see the :doc:`chapter on test bundles <../testbundles/alltestbundles>` to read how these are structured.

Sample Test-Bundle: Ping
************************

As an example, we now want to test if ``R1`` can ping ``R2``. Our sample test bundle then is as follows:

.. code:: yaml

  ---
  - test_module: pytest_nuts.base_tests.napalm_ping
    test_class: TestNapalmPing
    label: test1
    test_execution:
      count: 5
    test_data:
      - destination: 172.16.0.24
        expected: SUCCESS
        source: R1
        max_drop: 1

Note: 

* ``test_execution:`` By using the pre-defined key-value pair ``count: 5``, we indicate that the ping should be executed 5 times.
* ``test_data.expected: SUCCESS`` The pre-defined values are either SUCCESS, FAIL, or FLAPPING.
* ``test_data.max_drop: 1`` indicates what actually counts as SUCCESS ping.


We save this file as ``test-definition-ping.yaml``.

Run NUTS
--------

If everything is set up as shown above, run the test from your root folder with this command:

.. code:: shell

    $ pytest tests/test-definition-ping.yaml

The output should then inform you if the test succeeded or not.

