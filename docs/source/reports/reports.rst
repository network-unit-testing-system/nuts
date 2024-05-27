Test Reports with NUTS 
======================

Since NUTS is a Pytest plugin, users can take advantage of its robust ecosystem for test result reporting. Occasionally, the need to append additional information may arise.
To address this, NUTS provides a hook - ``pytest_nuts_single_result``. This hook is triggered in the single_result fixture, offering access to the ``nuts_context`` and the ``NutsResult`` object.

.. code:: python

    def pytest_nuts_single_result(request: FixtureRequest, nuts_ctx: NutsContext, result: NutsResult) -> None:
        ...

Embedding Properties into jUnit XML Report
------------------------------------------

The example below demonstrates how to incorporate additional properties into the jUnit XML report.

.. code:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <testsuites>
        <testsuite name="pytest" errors="0" failures="0" skipped="0" tests="15" time="0.050"
            timestamp="2024-05-27T08:43:13.722041" hostname="codespaces-d1d96a">
            <testcase classname="tests.showcase_test.test-expanse.yaml.TestExpanseCrew"
                name="test_name[0]" file="tests/showcase/showcase_expanse.py" line="79" time="0.000">
                <properties>
                    <property name="test_id" value="123" />
                    <property name="category" value="demo" />
                </properties>
            </testcase>


Incorporating Properties into the Test File
...........................................


By using ``test_extras``, it's possible to embed further data into a test bundle. The data are stored in the ``NutsContext`` but not internally utilized. 
For this example, we define the additional properties to be appended to each test case result in the XML.

.. code:: yaml

  - test_module: tests.showcase.showcase_expanse
    test_class: TestExpanseCrew
    test_extras:
      properties:
        test_id: 123
        category: demo
    test_data:
      - ship: rocinante
        name: "naomi nagata"
        role: engineer
        origin: belter


Hook Execution
..............

The ``pytest_nuts_single_result`` hook's logic can be implemented in confest.py. This function will be called for each test result.

.. code:: python

    @pytest.hookimpl(tryfirst=True)
    def pytest_nuts_single_result(request, nuts_ctx, result):
        test_extras = nuts_ctx.nuts_parameters.get("test_extras", {})
        for p_name, p_value in test_extras.get("properties", {}).items():
            request.node.user_properties.append((p_name, p_value))

If ``test_extras`` exists in the NUTS context, every key-value pair under the ``properties`` attribute will be appended to the Pytest node object and subsequently incorporated into the jUnit report.


Starting Pytest with the jUnit Option
.....................................

To embed properties into jUnit, the ``xunit1`` version should be used. Add the following to the Pytest configuration:

.. code:: ini

  [pytest]
  junit_family = xunit1

To generate the report, simply execute pytest using the ``--junit-xml=path`` option, which generates the junit xml report at the designated path.


.. code:: shell
  
  pytest --junit-xml=junit_report.xml
