.. NUTS - Network Unit Testing System documentation master file

Documentation of NUTS
=====================

Introduction
------------

The Network Unit Testing System or "nuts" in short draws on the concept of unit tests, known from the domain of programming, and applies it to the domain of networking.

One major difference between unit tests in programming and network tests is the definition of what a test actually is. 
In programming, unit tests normally focus on testing edge cases, since the amount of non-edge cases is not definable.
In the network testing domain, tests are less about edge cases, but more about testing existing network states with 
pre-defined test cases. Such a single test case might be "can host A reach neighbors X, Y, Z?" on many different devices. 
This is what nuts tries to achieve:
Apply test cases based on your pre-defined network topology to your actual network and have the tests confirm the correct state.


How nuts works
--------------

In order to run nuts, two components are required:

#. **Inventory of the network**.  Currently, these are YAML files in the form of a `nornir inventory <https://nornir.readthedocs.io/en/latest/tutorial/inventory.html>`__. They contain all details of your network, such as hosts, login information and other configuration. 

#. **Test bundles** in the form of YAML files that specify the actual tests. A test bundle is a series of tests that are logically related to each other. Each test bundle is structured in a similar way but has specific fields tailored to the test bundle. Some field values in a test bundle are directly related to your inventory.

Head over to the :doc:`Usage section <tutorial/firststeps>` to see how those two components are structured and how you get nuts up and running.

The project relies on the `pytest framework <https://docs.pytest.org/>`__ to set up and execute the
tests. Nuts itself is written as a custom pytest plugin. In the background, `nornir <https://nornir.readthedocs.io/>`__ executes specific network tasks for the actual tests.

Pytest reads in the test bundle (step 2 above) and transforms it into test runs. In the background, nornir uses the network information provided in the inventory (step 1 above), queries the network based on the specific test bundle and passes the results of those queries to pytest. Pytest then evaluates if the expectations defined in the test bundle match those results.

.. image:: images/nuts-ablauf-en.drawio.png
    :width: 800
    :alt: Nuts will take the YAML-test bundles and generate pytest test classes from them. These test classes will run the respective Nornir tasks and get the results from them in form of a Nornir 'MultiResult' or 'AggregatedResult' respectively. NUTS will provide these test results to the pytest test functions in form of 'NutsResult' instances.

Enhance nuts
------------
Nuts is written in Python and designed as a pytest plugin. It provides some base tests described in :doc:`the section about all test bundles <testbundles/alltestbundles>`, but since it's a plugin, you can write your own, self-written test classes for your custom tests. 
A dev documentation on how to write your own test classes is planned for a future release. 

You can write your own test classes! The ``nuts/base_tests`` folder in the code repository contains sample implementations and :doc:`the development section <dev/writetests>` has a short introduction.

Contents
========

.. toctree::
   :maxdepth: 2

   Home <self>
   Installation <installation/install>
   Tutorial <tutorial/firststeps>
   Test Bundles <testbundles/alltestbundles>
   Writing Custom Tests <dev/writetests>
   Test Reports <reports/reports>
   Advanced Options <advanced/cli>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
