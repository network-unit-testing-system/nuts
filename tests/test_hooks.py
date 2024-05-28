from pytest import Pytester
from xml.dom import minidom

from tests.utils import YAML_EXTENSION


def test_record_property(pytester: Pytester) -> None:
    pytester.makeconftest(
        """
            import pytest

            @pytest.hookimpl(tryfirst=True)
            def pytest_nuts_single_result(request, nuts_ctx, result):
                test_extras = nuts_ctx.nuts_parameters.get("test_extras", {})
                for p_name, p_value in test_extras.get("properties", {}).items():
                    request.node.user_properties.append((p_name, p_value))
            """
    )
    arguments = {
        "test_class_property": """
                        ---
                        - test_module: tests.showcase.showcase_expanse
                          test_class: TestExpanseCrew
                          test_extras:
                            properties:
                              test: pytest
                              test_nr: 123
                          test_data:
                            - ship: rocinante
                              name: "naomi nagata"
                              role: engineer
                              origin: belter
                        """,
    }
    pytester.makefile(YAML_EXTENSION, **arguments)

    result = pytester.runpytest("test_class_property.yaml")

    xml_path = pytester.path.joinpath("junit.xml")
    result = pytester.runpytest(f"--junitxml={xml_path}", "-o", "junit_family=xunit1")
    xmldoc = minidom.parse(str(xml_path))

    result.assert_outcomes(passed=3)
    testcases = xmldoc.getElementsByTagName("testcase")
    assert len(testcases) == 3
    for testcase in testcases:
        properties = testcase.getElementsByTagName("property")
        assert properties[0].getAttributeNode("name").value == "test"
        assert properties[0].getAttributeNode("value").value == "pytest"
        assert properties[1].getAttributeNode("name").value == "test_nr"
        assert properties[1].getAttributeNode("value").value == "123"
