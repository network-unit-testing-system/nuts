# NetTowel Network Unit Testing System

## Introduction

NetTowel Network Unit Testing System or short nuts is the testing component of the NetTowel Project.
It automates tests in the network similar to unit tests that you might know from programming.

One major difference between unit tests in programming and 
in the network is the count of how many times a single test should be executed.
In programming one normally focuses on testing the edge cases 
as the iteration of all possible data entries would not be possible.
In the network testing domain it is still true that not every possibility can be considered, 
however often one might want to test a single test case on many different devices.

The project is heavily based on the pytest framework.
It therefore acts as a custom pytest plugin.

One of the main concepts that is introduced in nuts is the separation of the test definition
and the so called test bundle.

The test definition is a pytest TestClass and is implemented in python.
A predefined set of test definitions can be found in the module base_tests, 
but new test definitions can be added easily by the user of the plugin.

The test bundle specifies which of the test definitions are executed and normally contains data which 
is used to determine which tests should be collected by pytest.
Even persons without python knowledge should be able to add new test bundles 
or update existing ones to reflect changes in the network. 

## Test bundle structure

Currently only yaml files are supported as test bundles, 
but other sources such as other file formats or database entries could be considered in later versions.

Each test bundle contains the following structure:
```yaml
---
- test_module: <module that contains the test class> # optional
  test_class: <name of the test class>
  label: <label to uniquely identify test> # optional 
  test_execution: <additional data used to execute the test> # optional
  test_data: <data that is used to generate the test cases>
...
```
`test_module`: The full path of the python module that contains the test class which should be used.
This value is optional if the test class is registered in index.py of the pytest-nuts plugin.
Note that it can be relevant in which directory `pytest` is started if local test modules are used.

`test_class`: The name of the python class which contains the tests that should be executed.
Note that currently every test in this class will be executed.

`label`: Additional identifier that can be used to distinguish between multiple occurrences of the same 
 test class in a test bundle.

`test_execution`: Data that is exposed as part of the `nuts_parameters` fixture. 
By conventions this contains additional information which will be passed directly to the called nornir task.

`test_data`: Data that will be used to parametrize the tests in the test class which have the `pytest.mark.nuts` annotation.
It is additionally exposed as a part of the `nuts_parameters` fixture.

### Examples
Example of a test bundle for TestNetmikoCdpNeighbors which tests that R1 is a CDP Neighbor of both R2 and R3.
This example will create three different tests, one for each entry in the test_data list.
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
## Exposed fixtures
TODO explain the exposed fixtures

## nuts custom marker
To use the data, which is defined in the test bundle, during the test collection a custom pytest marker "nuts" is used.
This annotation is a wrapper around the `pytest.mark.parametrize` annotation,
 but allows the plugin to consider the data entries from the test bundle.

For each entry in the `test_data` entry of the test bundle a single test case is generated.
As `pytest.mark.parametrize` expects a list of n-tuples as input but a more structured definition is to prefer in the test bundle,
the plugin transforms the entries from `test_data` into tuples.
This transformation is currently fixed, but more flexibility is very likely to come at a later stage.

Based on the first argument of the annotation the required fields are determined and for each entry in the `test_data`
these fields are extracted and transformed to a tuple considering the correct order.
Because of this, it is currently a requirement that each entry in the `test_data` is a dictionary.

### Example of test class with custom marker
```python
import pytest
class CdpNeighborTest:
    @pytest.mark.nuts("source,local_port,destination_host,management_ip,remote_port", "placeholder")
    def test_cdp_neighbor_partial(self, general_result, source, local_port, destination_host, remote_port):
        pass
```


## Installation as a user
NetTowel nuts is currently not published via pip it therefore has to be cloned and installed manually.

```
git clone ssh://git@bitbucket.ins.local:7999/ntw/nettowel-nuts.git
pip install <your_nuts_directory>
```

## Development
As a dependency manager [poetry](https://python-poetry.org/) is used.
If you have not installed poetry please consider their [documentation](https://python-poetry.org/docs/#installation)

### Install requirements

```bash
poetry install
```

### Open shell with venv

```bash
poetry shell
```

### SonarQube
The project is analysed on our [sonarqube server](sonarqube.ins.work) automatically via bamboo.
If you prefer to run your analysis without pushing you can trigger the analysis locally after executing the tests with coverage
WINDOWS PowerShell
```bash
$token=<your_token>
docker run --volume ${pwd}:/usr/src --workdir /usr/src --rm -e SONAR_HOST_URL="https://sonarqube.ins.work" -e SONAR_LOGIN=$token sonarsource/sonar-scanner-cli "-Dsonar.projectKey=nettowel-nuts" "-Dsonar.branch.name=$(git rev-parse --abbrev-ref HEAD)" "-Dsonar.python.coverage.reportPaths=/usr/src/test-reports/coverage.xml"
```
UNIX:
```bash
token=<your_token>
docker run --volume $PWD:/usr/src --workdir /usr/src --rm -e SONAR_HOST_URL="https://sonarqube.ins.work" -e SONAR_LOGIN=$token sonarsource/sonar-scanner-cli -Dsonar.projectKey=nettowel-nuts -Dsonar.branch.name=$(git rev-parse --abbrev-ref HEAD) -Dsonar.python.coverage.reportPaths=/usr/src/test-reports/coverage.xml
```
