.. NUTS - NetTowel Network Unit Testing System documentation master file

Documentation of NUTS
=====================

Introduction
------------

The NetTowel Network Unit Testing System or "NUTS" for short is the
testing component of the NetTowel Project, which is developed at the Institute of Networked Solutions in Rapperswil, Switzerland.
NUTS draws on the concept of unit tests, known from the domain of
software development, and applies it to the domain of networking.

One major difference between unit tests in software development and 
network tests is the definition of a test. 
In software development, unit tests normally focus on testing edge cases, 
since the amount of non-edge cases is not definable. 
In the network testing domain, tests are less about edge cases, but more about testing network functionalities with pre-defined test cases. Such a single test case might be "can host A
reach neighbors X, Y, Z?" or "has host A all BGP neighbors configured correctly?" on many different devices. 

This is what NUTS tries to achieve:
Use pre-defined test cases together with your network topology, apply this to your actual network and have the tests confirm that the network has the expected functionalities.

How NUTS works
--------------

In order to run NUTS, two components are required:

#. **Inventory of the network**.  Currently, these are YAML-files in the form of a `nornir inventory <https://nornir.readthedocs.io/en/latest/tutorial/inventory.html>`__. They contain all details of your network, such as hosts, login-information and other configuration. 

#. **Test bundles** in the form of YAML-files that specify the actual tests. A test bundle is a series of tests that are logically related to each other. Each test bundle is structured in a similar way, but has specific fields tailored to the test bundle. Some field values in a test bundle are directly related to your inventory.

Head over to the :doc:`Usage section <tutorial/firststeps>` to see how those two components are structured and how you get NUTS up and running.

The project relies on the `pytest framework <https://docs.pytest.org/>`__ to setup and execute the
tests. NUTS itself is written as a custom pytest plugin. In the background, `nornir <https://nornir.readthedocs.io/>`__ executes specific network tasks for the actual tests.

Pytest reads in the test bundle (2.) and transforms it into test runs. In the background, nornir uses the network information provided in the inventory (1.), queries the network based on the specific test bundle and passes the results of those queries to pytest. Pytest then evaluates if the expectations defined in the test bundle match those results.

Enhance NUTS
------------
Since NUTS is written as a pytest plugin and in python, you can customize it yourself and write your own test classes. Please see the :doc:`development section <dev/index>` to see how NUTS is structured and how to write your own test classes.


Contents
========

.. toctree::
   :maxdepth: 2

   Home <self>
   Installation <installation/index>
   Tutorial <tutorial/firststeps>
   Test Bundles <testbundles/alltestbundles>
   Development <dev/index>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
