# NetTowel Network Unit Testing System

## Introduction

The NetTowel Network Unit Testing System or "nuts" in short is the testing component of the NetTowel Project.
It draws on the concept of unit tests, known from the domain of programming, and applies it to the domain of networking.

One major difference between unit tests in programming and 
network tests is the definition of what a test actually is. 
In programming, unit tests normally focus on testing edge cases, 
since the amount of non-edge cases is not definable.
In the network testing domain, tests are less about edge cases, but more about testing existing configurations with 
pre-defined test cases. Such a single test case might be "can host A reach neighbors X, Y, Z?" on many different devices. 
This is what nuts tries to achieve:
Apply test cases based on your pre-defined network topology to your actual network and have the tests confirm
the correct configuration.

The project relies on the [pytest framework](https://docs.pytest.org/) to setup and execute the tests. 
Nuts itself is written as a custom pytest plugin. In the background, [nornir](https://nornir.readthedocs.io/) 
executes specific network tasks for the actual tests.

Additionally, nuts treats the test definition and the so-called test bundle as separate entities.

The test definition is modelled as a custom `pytest.Class`, and a predefined set of test definitions can be found 
in the module `base_tests`. New test definitions can be added easily by the user of the plugin.

The test bundle is a file that is parsed by pytest. The file provides data on the actual network configuration and 
describes which test definitions should be collected and executed by pytest. 
The structure of the test bundle should enable people without in-depth python knowledge to add new test bundles 
or update existing ones to reflect changes in the network. 

## Test bundle structure

Currently only yaml files are supported as test bundles, 
but other sources such as other file formats or database entries can be considered in later versions.

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
This value is optional if the test class is registered in index.py of the pytest-nuts plugin.
Note that it can be relevant in which directory `pytest` is started if local test modules are used.

`test_class`: The name of the python class which contains the tests that should be executed.
Note that currently every test in this class will be executed.

`label`: Additional identifier that can be used to distinguish between multiple occurrences of the same 
 test class in a test bundle.

`test_execution`: Data that is exposed as part of the `nuts_parameters` fixture. 
By convention this contains additional information that is passed directly to the nornir task in the background. 
Therefore the key-value pairs must be consistent with the key-value pairs of the specific nornir task. 
As an example, the test definition `napalm_ping.py` calls a nornir task to execute napalm's ping-command. 
This allows the additional `max_drop` parameter in `test execution`, since it is in turn pre-defined by napalm.

`test_data`: Data that is used to parametrize the tests in the test class which have the `pytest.mark.nuts` annotation.
It is additionally exposed as a part of the `nuts_parameters` fixture.

### Examples
Example of a test bundle for `TestNetmikoCdpNeighbors` which tests that `R1` is a CDP Neighbor of both `R2` and `R3`.
This example creates three different tests, one for each entry in the `test_data` list.

```yaml
---
- test_module: pytest_nuts.base_tests.netmiko_cdp_neighbors
  test_class: TestNetmikoCdpNeighbors
  test_data:
    - source: R1
      local_port: GigabitEthernet3
      destination_host: R2
      management_ip: 172.16.12.2
      remote_port: GigabitEthernet2
    - source: R1
      local_port: GigabitEthernet4
      destination_host: R3
      management_ip: 172.16.13.3
      remote_port: GigabitEthernet2
    - source: R2
      local_port: GigabitEthernet2
      destination_host: R1
      management_ip: 172.16.12.1
      remote_port: GigabitEthernet3
...
```

## Installation instructions
NetTowel nuts is currently not published via pip. It has to be cloned and installed manually.

```
git clone ssh://git@bitbucket.ins.local:7999/ntw/nettowel-nuts.git
pip install <your_nuts_directory>
```

## Technical details

### Exposed fixtures
The predefined test cases use [nornir](https://nornir.readthedocs.io/en/latest/) in order to 
communicate with the network devices.
To reduce the complexity of the test classes, nuts defers the execution of the tasks to nornir and 
only evaluates the results.

Because the execution of these tasks is always similar, there exist pre-defined fixtures that are used by every 
test class. Each of these fixtures can be overwritten with a test-specific fixture in the test class itself. 
Theses pre-defined fixtures are as follows:

`general_result`: Runs a nornir task on the inventory and returns the result. 
Requires `nr`, `nuts_task`, `nuts_arguments` and `nornir_filter` as input parameters.
 
`nr`: The nornir instance that should be used when executing the nornir task.
Defaults to a simple nornir instance that uses `nornir_config_file` as its configuration.

`nornir_config_file`: The location of the nornir configuration file as a string. Is used by `nr` to instantiate nornir.
Note that it can be relevant in which directory `pytest` is started if this is a relative path.
Defaults to `nr-config.yaml`.

`nornir_filter`: A nornir filter that is applied to the `nr` instance before the task is executed, 
for example to filter for specific hosts. Defaults to an empty filter so that the task runs on the full instance.

`nuts_arguments`: Arguments that are passed to the nornir task as `kwargs`. These can be  
parameters that are defined in the `test_execution` part of the test bundle. 
Defaults to an empty dictionary so that no data is passed to the task.

If you read this carefully, you might have noticed that `general_result` requires `nuts_task`, but it is not exposed by default.
It is the job of the test class to expose the appropriate nornir task as the `nuts_task` fixture as there is no viable default task.

In addition to these statically exposed fixtures, `nuts_parameters` is exposed 
when pytest is called on yaml files (see "Test Bundle Structure".

### Nuts custom marker
During test collection, the custom pytest marker "nuts" uses the data that has been defined in the test bundle.
This annotation is a wrapper around the `pytest.mark.parametrize` annotation and allows the plugin to 
consider the data entries from the test bundle.

The custom marker generates a single test case for each entry in the `test_data` section of the test bundle.
Since `pytest.mark.parametrize` expects a list of n-tuples as input, but the test bundle requires a different structure, 
the plugin transforms the entries from `test_data` into tuples.
This transformation is currently fixed, but more flexibility is very likely to come at a later stage.

Based on the first argument of the annotation the required fields are determined and for each entry in `test_data`
these fields are extracted and transformed to a tuple considering the correct order.
Because of this, it is currently a requirement that each entry in the `test_data` is a dictionary.

#### Example of a test class with custom marker
```python
import pytest
class CdpNeighborTest:
    @pytest.mark.nuts("source,local_port,destination_host,management_ip,remote_port", "placeholder")
    def test_cdp_neighbor_partial(self, general_result, source, local_port, destination_host, remote_port):
        pass
```



## Development
Nuts uses [poetry](https://python-poetry.org/) as a dependency manager.
If you have not installed poetry, please read their [installation instructions](https://python-poetry.org/docs/#installation).

### Installation requirements

```bash
poetry install
```

### Open Shell with venv

```bash
poetry shell
```

### SonarQube
Our [sonarqube server](sonarqube.ins.work) automatically analyses our project via bamboo.
If you prefer to run your analysis without pushing you can trigger the analysis locally after executing the tests with coverage.

Windows PowerShell:
```bash
$token=<your_token>
docker run --volume ${pwd}:/usr/src --workdir /usr/src --rm -e SONAR_HOST_URL="https://sonarqube.ins.work" -e SONAR_LOGIN=$token sonarsource/sonar-scanner-cli "-Dsonar.projectKey=nettowel-nuts" "-Dsonar.branch.name=$(git rev-parse --abbrev-ref HEAD)" "-Dsonar.python.coverage.reportPaths=/usr/src/test-reports/coverage.xml"
```
UNIX:
```bash
token=<your_token>
docker run --volume $PWD:/usr/src --workdir /usr/src --rm -e SONAR_HOST_URL="https://sonarqube.ins.work" -e SONAR_LOGIN=$token sonarsource/sonar-scanner-cli -Dsonar.projectKey=nettowel-nuts -Dsonar.branch.name=$(git rev-parse --abbrev-ref HEAD) -Dsonar.python.coverage.reportPaths=/usr/src/test-reports/coverage.xml
```