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

The project is heavily based on the pytest framework and uses Nornir to fetch data from the network devices.
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

Currently only yaml files are supported as test bundles, 
but other sources such as other file formats or database entries could be considered in later versions.

## Examples

TODO add examples

## Installation as a user
NetTowel nuts is currently not published via pip it therefore has to be cloned and installed manually.

```
git clone ssh://git@bitbucket.ins.local:7999/ntw/nettowel-nuts.git
pip install <your_nuts_directory>
```

## Technical information
To use the data, which is defined in the test bundle, during the test collection a custom pytest mark "nuts" is used.
This annotation is similar to the `pytest.mark.parametrize` annotation and allows to specify which data from the test bundle is used.
For each entry in the 'test_data' entry of the test bundle a single test case is generated and for each entry the corresponding values are extracted  
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
