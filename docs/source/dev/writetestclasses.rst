How To Write Your Own Test
==========================

Nuts is written as a `pytest plugin <https://docs.pytest.org/en/6.2.x/writing_plugins.html`__ and allows you to write your own tests, apart from the existing ones in ``nuts/base_tests``. 

**IMPORTANT NOTE**: If you plan on writing your own tests, please be aware that nuts 4.0 will probably introduce major breaking changes. This means: The code you write for nuts version 3 will most probably NOT work for version 4. We briefly provide here the necessary steps for the curious ones and those who are willing to experiment. 

A Simple Test 
-------------

There exists a showcase that displays the most basic test possible, one that also works without a network to gather data. You find the module that contains the code in ``tests/showcase`` and the test bundle (the YAML file)  in ``tests/showcase_test``. 

The Test itself
...............

Three classes are needed for a test:

1. Context class: Holds all necessary information that is needed for a specific test. Yields the raw, unprocessed result. Base class: ``NutsContext``
2. Extractor class: Processes the raw overall results from a network query (mostly a nornir task), so that it can be passed on to the test class. Base class: ``AbstractResultExtractor``
3. Test class: The actual tests that test data from the YAML file against the retrieved, processed data from the network.

The showcase test implements therefore three classes and the necessary methods:

1. ``ExpanseContext`` derives from ``NutsContext``. The context to be used by nuts is defined by setting ``CONTEXT = ExpanseContext``.
2. ``class ExpanseExtractor`` derives from ``AbstractResultExtractor``
3. ``class TestExpanseCrew`` is the actual test class

Here's a code snippet from ``class TestExpanseCrew`` to illustrate how the test class is written:

.. code:: python

    class TestExpanseCrew:
    # ...
    @pytest.mark.nuts("name, role")
    def test_role(self, single_result: NutsResult, name: str, role: str) -> None:
        assert single_result.result[name]["role"] == role

``@pytest.mark.nuts("name, role")`` is a custom pytest marker: The arguments ``name, role`` refer to the fields as they are defined in the YAML file under ``test_data``. They are then passed on as a pytest fixture to the test itself.

The YAML-File
.............

You can then proceed to write a sample YAML file that uses the test:

    * ``test_module`` directly refers to your module and its location.
    * ``test_class`` is the name of the test class you have defined in step 3 in the previous section.
    * ``test_data`` contains the data against which the tests should be run. Be aware that the fields under ``test_data`` and those used in the test itself must match. 

Fields in ``test_data`` are optional except for the key into the results (``ship`` in our case here, usually ``host``). If you leave out other fields than the key, the test that requires that particular entry will be skipped. The following snipped comments out ``origin``, which therefore skips ``test_origin()`` for Bobbie Draper.

.. code:: yaml

    - ship: rocinante
      name: "bobbie draper"
      role: marine
      # origin: mars


A Test Using Nornir
-------------------
To illustrate how this test works, we use the BGP test (``nuts/base_tests/napalm_bgp_neighbors.py``). The test implements the three classes:

    1. ``BgpNeighborsContext`` derives from ``NornirNutsContext``.
    2. ``BgpNeighborsExtractor`` derives from ``AbstractHostResultExtractor``
    3. ``class TestNapalmBgpNeighborsCount`` is the actual test class

The context to be used is defined by setting ``CONTEXT = BgpNeighborsContext``. This time, we need to connect to a network and do not directly derive from ``NutsContext``, but rather from ``NornirNutsContext``. This requires the setup of a nornir inventory too - Please see :doc:`First Steps with NUTS <../tutorial/firststeps>` for more information.

There is an important distinction on what kind of extractor you want to derive from. Basically, there are to broad type of tests in nuts: (1) test properties of a host and (2) test connection properties between two hosts. Examples of (1) are nearly all test bundles in nuts including the BGP test, example of (2) are the ping and iperf tests. These two types determine from which extractor you want to derive:

    1. Test host properties: Derive from ``AbstractHostResultExtractor``
    2. Test connection properties: Derive from ``AbstractHostDestResultExtractor``

The test class is written very similar to the simple case above: Set the pytest custom marker with the required arguments, use them as fixture and write the test.



