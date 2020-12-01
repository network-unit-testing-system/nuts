Test Bundles
============

You find here all network tests that have been implemented in NUTS. They can be executed with the command ``$ pytest <test>.yaml``. Note that you need an inventory for the tests to work, and some fields in the bundles directly refer to items in that inventory. Please see the :doc:`First Steps with NUTS <../tutorial/firststeps>` for more information.

You can also set a ``label`` field in your test bundles. Since this field is not necessary, we omitted it in the examples.

In some test bundles you can directly pass arguments to the network query that is executed in the background. For this reason, we indicate for each test bundle the specific network library and its command that is used to query the devices. The libraries used so far are `napalm <https://napalm.readthedocs.io/en/latest/>`__ and `netmiko <https://ktbyers.github.io/netmiko/>`__.


BGP Neighbors
-------------

**Test Bundle:** Tests if pre-defined BGP neighbors exist on a host.

**Library used:** `Napalm-Get <https://github.com/napalm-automation/napalm/blob/master/napalm/base/base.py>`__.

**Test Bundle Structure**

.. code:: yaml

    ---
    - test_module: pytest_nuts.base_tests.napalm_bgp_neighbors
      test_class: TestNapalmBgpNeighbors
      test_data:
        * source: <host name as defined in inventory>
          local_id: <id>
          local_as: <AS number>
          peer: <IP address>
          remote_as: <AS number>
          remote_id: <remote ID>
          is_enabled: <true|false>
          is_up: <true|false>


**Test Bundle Example**

.. code:: yaml

    ---
    - test_module: pytest_nuts.base_tests.napalm_bgp_neighbors
      test_class: TestNapalmBgpNeighbors
      test_data:
        - source: R1
          local_id: 172.16.255.1
          local_as: 45001
          peer: 172.16.255.2
          remote_as: 45002
          remote_id: 0.0.0.0
          is_enabled: true
          is_up: false

CDP Neighbors
-------------

**Test Bundle:** Tests if pre-defined CDP neighbors exist on a host.

**Library used:** `Netmiko-Send <https://github.com/ktbyers/netmiko/blob/develop/netmiko/base_connection.py>`__.

**Test Bundle Structure**

.. code:: yaml

    ---
    - test_module: pytest_nuts.base_tests.netmiko_cdp_neighbors
      test_class: TestNetmikoCdpNeighbors
      test_data:
        - source: <host name as defined in inventory>
          local_port: <name of the local port>
          destination_host: <host name as defined in inventory>
          management_ip: <IP address
          remote_port: <name of the remote port>


**Test Bundle Example**

.. code:: yaml

    ---
    - test_module: pytest_nuts.base_tests.netmiko_cdp_neighbors
      test_class: TestNetmikoCdpNeighbors
      test_data:
        - source: R1
          local_port: GigabitEthernet3
          destination_host: R2
          management_ip: 172.16.12.2
          remote_port: GigabitEthernet2


LLDP Neighbors
--------------

CDP Neighbors
-------------

**Test Bundle:** Tests if pre-defined LLDP neighbors exist on a host.

**Library used:** `Netmiko-Send <https://github.com/ktbyers/netmiko/blob/develop/netmiko/base_connection.py>`__.

**Test Bundle Structure**

.. code:: yaml

    ---
    - test_module: pytest_nuts.base_tests.netmiko_cdp_neighbors
      test_class: TestNetmikoCdpNeighbors
      test_data:
        - source: <host name as defined in inventory>
          local_port: <name of the local port>
          destination_host: <host name as defined in inventory>
          management_ip: <IP address
          remote_port: <name of the remote port>


**Test Bundle Example**

.. code:: yaml

    ---
    - test_module: pytest_nuts.base_tests.napalm_lldp_neighbors
      test_class: TestNapalmLldpNeighbors
      label: test1
      test_execution:
      test_data:
        - source: R1
          local_port: GigabitEthernet3
          remote_host: R2
          remote_port: GigabitEthernet2


OSPF Neighbors
--------------





Network Instances
-----------------



Network Interfaces
------------------



Ping Hosts
----------




Users on a Device
-----------------



