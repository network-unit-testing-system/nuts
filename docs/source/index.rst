.. NUTS - NetTowel Network Unit Testing System documentation master file, created by
   sphinx-quickstart on Tue Nov 24 09:43:45 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation of NUTS
=====================

Introduction
------------

The NetTowel Network Unit Testing System or "NUTS" in short is the
testing component of the NetTowel Project developed at the Institute of Networked Solutions in Rapperswil, Switzerland.
It draws on the concept of unit tests, known from the domain of
programming, and applies it to the domain of networking.

One major difference between unit tests in programming and 
network tests is the definition of what a test actually is. 
In programming, unit tests normally focus on testing edge cases, 
since the amount of non-edge cases is not definable. 
In the network testing domain, tests are less about edge cases, but more about testing existing configurations with pre-defined test cases. Such a single test case might be "can host A
reach neighbors X, Y, Z?" on many different devices. 

This is what NUTS tries to achieve:
Apply test cases based on your pre-defined network topology to your actual network and have the tests confirm the correct configuration.

How NUTS works
--------------

In order to run NUTS, you need the following components:

1. **Test bundles** in the form of YAML-files that specify the actual tests. Each test bundle is structured in a similar way, but has specific fields tailored to the test bundle. 

2. **Information on your network**. Currently, these are YAML-files in the form of a `nornir inventory <https://nornir.readthedocs.io/en/latest/tutorial/inventory.html>`__. They contain all details of your network, such as hosts, login-information and other configuration. 

Head over to the :doc:`Usage section <tutorial/firststeps>` to see how those two components are structured and how you get NUTS up and running.

The project relies on the `pytest framework <https://docs.pytest.org/>`__ to setup and execute the
tests. NUTS itself is written as a custom pytest plugin. In the background, `nornir <https://nornir.readthedocs.io/>`__ executes specific network tasks for the actual tests.

Pytest reads in the test bundle (1.) and transforms it into test runs. In the background, nornir uses the network information provided in (2.), queries the network based on the specific test bundle and passes the results of those queries to pytest. Pytest then evaluates if the expectations in the test bundle match those results.

Enhance NUTS
------------
Since NUTS is written as a pytest plugin and in python, you can customize it yourself. Please see the :doc:`Develop section <dev/index>` to see how NUTS is structured and how you can write your own test bundles. The :doc:`API section <api/index>` contains the auto-generated docstrings of the project.



Contents
========

.. toctree::
   :maxdepth: 2

   Home <self>
   Installation <installation/index>
   Tutorial <tutorial/firststeps>
   Test Bundles <testbundles/alltestbundles>
   Develop <dev/index>
   API <api/index>




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
