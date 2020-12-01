Test Bundles
============

A test bundle contains one ore more tests that are related to each other. For example, when executing the test bundle that checks BGP neighbors, a test of that bundle checks the correctness of the local ID, another checks if a peer is up etc.

You find here all network test bundles that have been implemented in NUTS. They can be executed with the command ``$ pytest <test>.yaml``. Note that you need an inventory for the tests to work, and some fields in the bundles directly refer to items in that inventory. Also, there are optional fields in test bundles, e.g. the ``label`` field, those have been omitted for clarity. Please see :doc:`First Steps with NUTS <../tutorial/firststeps>` for more information.

In some test bundles you can directly pass arguments to the network query that is executed in the background. For those test bundles we indicate the specific network library and the command that is used to query the devices, so that you see all available arguments. The libraries used are `napalm <https://napalm.readthedocs.io/en/latest/>`__ and `netmiko <https://ktbyers.github.io/netmiko/>`__.

BGP Neighbors - Information
---------------------------

**Test Bundle:** Tests if pre-defined BGP neighbors exist on a host.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_bgp_neighbors
      test_class: TestNapalmBgpNeighbors
      test_data:
        - source: <host name, required>
          local_id: <ID>
          local_as: <AS number>
          peer: <IP address, required>
          remote_as: <AS number>
          remote_id: <remote ID>
          is_enabled: <true|false>
          is_up: <true|false>

Required fields for specific tests in this bundle:

    * Test the local AS: ``source, peer, local_as`` 
    * Test the local ID: ``source, peer, local_id``
    * Test remote AS: ``source, peer, remote_as``
    * Test remote ID: ``source, peer, remote_id``
    * Test if the peer is enabled: ``source, peer, is_enabled``
    * Test if the peer is up: ``source, peer, is_up``

If all fields are present, all tests are executed. If the field is missing, the test is skipped: In the example below, ``R2`` only has a test that checks if its neighbor is down (``is_up: false``).

**Test Bundle Example**

.. code:: yaml

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
        - source: R2
          peer: 172.16.255.2
          is_up: false      


BGP Neighbors - Count
---------------------

**Test Bundle:** Tests the amount of BGP neighbors a host should have.

**Library used:** `Napalm <https://github.com/napalm-automation/napalm>`__.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_bgp_neighbors
      test_class: TestNapalmBgpNeighborsCount
      test_data:
        - source: <host name, required>
          neighbor_count: <number of neighbors, required>


**Test Bundle Example**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_bgp_neighbors
      test_class: TestNapalmBgpNeighborsCount
      test_data:
        - source: R1
          neighbor_count: 2
        - source: R2
          neighbor_count: 1


CDP Neighbors
-------------

**Test Bundle:** Tests if pre-defined CDP neighbors exist on a host.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.netmiko_cdp_neighbors
      test_class: TestNetmikoCdpNeighbors
      test_data:
        - source: <host name, required>
          local_port: <name of the local interface>
          destination_host: <host name, required>
          management_ip: <IP address>
          remote_port: <name of the remote interface>

Required fields for specific tests in this bundle:

    * Test destination host: ``source, destination_host`` 
    * Test local port: `` source, destination_host, local_port``
    * Test remote port: ``destination_host, remote_port``
    * Test management IP: ``source, destination_host, management_i``

**Test Bundle Example**

.. code:: yaml

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

**Test Bundle:** Tests if pre-defined LLDP neighbors exist on a host.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_lldp_neighbors
      test_class: TestNapalmLldpNeighbors
      test_data:
        - source: <host name, required>
          local_port: <name of the local interface, required>
          remote_host: <host name>
          remote_port: <name of the remote interface>

Required fields for specific tests in this bundle:

    * Test remote host: ``local_port, remote_host``
    * Test remote port: ``local_port, remote_port`` 

**Test Bundle Example**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_lldp_neighbors
      test_class: TestNapalmLldpNeighbors
      test_data:
        - source: R1
          local_port: GigabitEthernet3
          remote_host: R2
          remote_port: GigabitEthernet2


OSPF Neighbors - Information
----------------------------

**Test Bundle:** Tests if pre-defined OSPF neighbors exist on a host.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.netmiko_ospf_neighbors
      test_class: TestNetmikoOspfNeighbors
      test_data:
        - source: <host name, required>
          local_port: <name of the local interface, required>
          neighbor_id: <ID>
          state: <FULL/BDR|FULL/DR>
          neighbor_address: <IP address>

Required fields for specific tests in this bundle:

    * Test neighbor ID: ``source, neighbor_id``
    * Test local port: ``source, local_port, neighbor_id``
    * Test neighbor address: ``source, neighbor_id, neighbor_address``
    * Test state: ``source, neighbor_id, state``


**Test Bundle Example**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.netmiko_ospf_neighbors
      test_class: TestNetmikoOspfNeighbors
      test_data:
        - source: GigabitEthernet2
          local_port: 172.16.255.3
          neighbor_id: 172.16.255.4
          state: FULL/BDR
          neighbor_address: 172.16.14.4


OSPF Neighbors - Count
----------------------------

**Test Bundle:** Tests the amount of OSPF neighbors a host should have.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.netmiko_ospf_neighbors
      test_class: TestNetmikoOspfNeighborsCount
      test_data:
        - source: <host name, required>
          neighbor_count: <number of neighbors, required>

**Test Bundle Example**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.netmiko_ospf_neighbors
      test_class: TestNetmikoOspfNeighbors
      test_data:
        - source: R1
          neighbor_count: 3


Network Instances
-----------------

**Test Bundle:** 

**Test Bundle Structure**

Required fields for specific tests in this bundle:

    * Test : ``something`` 


**Test Bundle Example**

Ping Hosts
----------

**Test Bundle:** 

**Test Bundle Structure**

Required fields for specific tests in this bundle:

    * Test : ``something`` 


**Test Bundle Example**


User Information
----------------


**Test Bundle:** Tests the if pre-defined users exist on a device.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_get_users
      test_class: TestNapalmUsers
      test_data:
        - host: <host name, required>
          username: <name>
          password: <password>
          level: <1...15>          

Required fields for specific tests in this bundle:

    * Test username: ``host, username``
    * Test password: ``host, username, password`` 
    * Test privilege level: ``host, username, level`` 

**Test Bundle Example**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_get_users
      test_class: TestNapalmUsers
      test_data:
        - host: R1
          username: arya
          password: stark
          level: 15

No Rogue Users
--------------

**Test Bundle:** Tests if only pre-defined users exist on a device, i.e. there are no rogue users.

**Test Bundle Structure**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_get_users
      test_class: TestNapalmOnlyDefinedUsersExist
      test_data:
        - host: <host name, required>
          usernames: <list of usernames, required>
            - <username>

**Test Bundle Example**

.. code:: yaml

    - test_module: pytest_nuts.base_tests.napalm_get_users
      test_class: TestNapalmOnlyDefinedUsersExist
      test_data:
        - host: R1
          usernames:
            - cisco
            - arya