BGP Neighbors
=============

Test Bundle Structure
---------------------

.. code:: yaml

  ---
  - test_module: pytest_nuts.base_tests.napalm_bgp_neighbors
    test_class: TestNapalmBgpNeighbors
    test_data:
      - source: <host name as defined in inventory>
        local_id: <id>
        local_as: <AS number>
        peer: <IP address>
        remote_as: <AS number>
        remote_id: <remote ID>
        is_enabled: <true|false>
        is_up: <true|false>


TEst
