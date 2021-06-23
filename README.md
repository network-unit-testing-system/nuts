# NetTowel Network Unit Testing System

## Introduction

The NetTowel Network Unit Testing System or "nuts" in short is the testing component of the NetTowel Project, which is developed at the Institute of Networked Solutions in Rapperswil, Switzerland.
It draws on the concept of unit tests, known from the domain of programming, and applies it to the domain of networking.

One major difference between unit tests in programming and 
network tests is the definition of what a test actually is. 
In programming, unit tests normally focus on testing edge cases, 
since the amount of non-edge cases is not definable.
In the network testing domain, tests are less about edge cases, but more about testing existing network states with 
pre-defined test cases. Such a single test case might be "can host A reach neighbors X, Y, Z?" on many different devices. 
This is what nuts tries to achieve:
Apply test cases based on your pre-defined network topology to your actual network and have the tests confirm the correct state.

## Installation Instructions

### Using pip

Run `pip install nuts` 

### Using poetry

Nuts uses [poetry](https://python-poetry.org/) as a dependency manager.

1. [Install poetry](https://python-poetry.org/docs/#installation).
2. Clone this repository.
3. Run `$ poetry install`

## How It Works: Test Bundles and Test Definitions

The project relies on the [pytest framework](https://docs.pytest.org/) to setup and execute the tests. 
Nuts itself is written as a custom pytest plugin. In the background, [nornir](https://nornir.readthedocs.io/) 
executes specific network tasks for the actual tests.

Nuts treats the test definition and the so-called test bundle as separate entities. The *test definition* is modeled as a custom `pytest.Class`, and a predefined set of test definitions can be found in the nuts module `base_tests`. New test definitions can be added easily by the user of the plugin.

The *test bundle* is a file that is parsed by pytest. The file provides data on the desired network state and describes which test definitions should be collected and executed by pytest. 
The structure of the test bundle should enable people without in-depth python knowledge to add new test bundles or update existing ones to reflect changes in the network. 

While the readme here is only a short overview, find the [documentation of nuts on readthedocs](https://nuts.readthedocs.io/en/latest/).

### Test Bundle Structure

Currently only yaml files are supported as test bundles, 
but other sources such as other file formats or database entries can be considered in later nuts versions.

Each test bundle contains the following structure:
```yaml
---
- test_module: <module that contains the test class> # optional
  test_class: <name of the test class>
  label: <label to uniquely identify the test> # optional 
  test_execution: <additional data used to execute the test> # optional
  test_data: <data used to generate the test cases>
...
```
`test_module`: The full path of the python module that contains the test class to be used.
This value is optional if the test class is registered in `index.py` of the pytest-nuts plugin.
Note that it can be relevant in which directory `pytest` is started if local test modules are used. Using `test_modules` allows you to write your own test classes. **Note: We currently do not support self-written test modules, since upcoming refactorings might introduce breaking changes.**

`test_class`: The name of the python class which contains the tests that should be executed.
Note that currently every test in this class will be executed.

`label`: Additional identifier that can be used to distinguish between multiple occurrences of the same 
 test class in a test bundle.

`test_execution`: Data that is exposed as part of the `nuts_parameters` property. 
By convention this contains additional information that is passed directly to the nornir task in the background. 
Therefore the key-value pairs must be consistent with the key-value pairs of the specific nornir task. 
As an example, the test definition `napalm_ping.py` calls a nornir task to execute napalm's ping-command. 
This allows the additional `max_drop` parameter in `test_execution`, since it is in turn pre-defined by napalm.

`test_data`: Data that is used to parametrize the tests in the test class which have the `pytest.mark.nuts` annotation. It is additionally part of the `nuts_parameters` property.

### Example: CDP Neighbors
Example of a test bundle for `TestNetmikoCdpNeighbors` which tests that `R1` is a CDP Neighbor of both `R2` and `R3`.
This example creates three different tests, one for each entry in the `test_data` list.

```yaml
---
- test_module: nuts.base_tests.netmiko_cdp_neighbors
  test_class: TestNetmikoCdpNeighbors
  test_data:
    - host: R1
      local_port: GigabitEthernet3
      destination_host: R2
      management_ip: 172.16.12.2
      remote_port: GigabitEthernet2
    - host: R1
      local_port: GigabitEthernet4
      destination_host: R3
      management_ip: 172.16.13.3
      remote_port: GigabitEthernet2
    - host: R2
      local_port: GigabitEthernet2
      destination_host: R1
      management_ip: 172.16.12.1
      remote_port: GigabitEthernet3
...
```

### How the Test Bundle Is Converted to a Pytest Test

When nuts is executed, pytest converts the test bundles (the yaml files) into tests. During test collection, the custom pytest marker `nuts` uses the data that has been defined in the test bundle mentioned above. 
This annotation is a wrapper around the `pytest.mark.parametrize` annotation and allows the plugin to use the data entries from the test bundle. For each entry in the `test_data` section of the test bundle, the custom marker generates a single test case. To achieve this, the plugin transforms the entries into n-tuples, since `pytest.mark.parametrize` expects a list of n-tuples as input. 

The custom nuts marker takes two arguments: The first argument of the annotation determines the required fields. 
For each entry in `test_data` these fields are extracted and transformed to a tuple considering the correct order.
If any of these fields are not present in an entry of `test_data`, the corresponding test case will be skipped.
A second argument determines optional fields that can also be used in a test case as well - non-present values are passed into the function as `None`.

The following test-run of CDP neighbors for example checks the local port:

```python
class TestNetmikoCdpNeighbors:       
    @pytest.mark.nuts("remote_host,local_port")
    def test_local_port(self, single_result, remote_host, local_port):
        assert single_result.result[remote_host]["local_port"] == local_port        
```


The required fields are `host`, `remote_host` and `local_port` - they must be present in the custom marker, 
but also be provided as argument to the test method itself.

`single_result` uses the `host` field and provides the result that has been processed via the specific context of a test.

### Test classes and their context
Each test module implements a context class to provide module-specific functionality to its tests. This context class is a  `NutsContext` or a subclass of it. 
This guarantees a consistent interface across all tests for test setup and execution. 
Currently, the predefined test classes use [nornir](https://nornir.readthedocs.io/en/latest/) in order to communicate 
with the network devices. Those test classes derive all from a more specific `NornirNutsContext`, 
which provides a nornir instance and nornir-specific helpers. In the example above, it is a class called `CdpNeighborsContext` that derives from `NornirNutsContext`.

If you want to learn more how nuts works but do not have a running network in the background, there's a nuts showcase - an offline test class that displays the basic functionality of nuts. See the [tutorial](https://nuts.readthedocs.io/en/latest/tutorial/firststeps.html) for further information.

## Develop Your Own Test Classes

Nuts is essentially designed as a pytest-plugin and it is possible to add your own, self-written test classes. 
A dev documentation on how to write your own test classes is planned for a future release.
Still, it is possible to write your own test classes nevertheless, even if we cannot guarantee that upcoming planned refactorings  do not introduce breaking changes.

## Community-provided test classes

* [Cisco IOSXE Test Class](https://github.com/briantsaunders/nuts-cisco-iosxe-tests) by [briantsaunders](https://github.com/briantsaunders)

# Thanks

* [Matthias Gabriel](https://github.com/MatthiasGabriel), who laid the foundations of nuts.
* [Florian Bruhin (The Compiler)](https://github.com/The-Compiler) for invaluable feedback and advice.
