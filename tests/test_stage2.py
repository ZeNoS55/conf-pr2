"""Unit tests for Stage 2: NuGet direct dependencies collection."""

import tempfile
import unittest
from unittest.mock import MagicMock, patch
from src.collector import (
    extract_deps_from_groups,
    fetch_nuget_dependencies,
    get_direct_dependencies,
    parse_nuspec_content,
    parse_test_repo_file,
)

EXPECTED_COUNT_TWO = 2
EXPECTED_COUNT_THREE = 3


class TestStage2Collector(unittest.TestCase):
    """Test suite for NuGet dependencies extractor."""

    def test_extract_deps_from_groups(self) -> None:
        """Test extracting dependencies across target framework groups."""
        groups = [
            {
                "targetFramework": "net8.0",
                "dependencies": [
                    {"id": "Serilog", "range": "[4.0.0, )"},
                    {"id": "Microsoft.Extensions.Hosting", "range": "8.0.0"},
                ],
            },
            {
                "targetFramework": "netstandard2.0",
                "dependencies": [
                    {"id": "Serilog", "range": "[3.0.0, )"},
                ],
            },
        ]
        deps = extract_deps_from_groups(groups)
        self.assertEqual(len(deps), EXPECTED_COUNT_TWO)
        self.assertIn("Serilog", deps)
        self.assertIn("Microsoft.Extensions.Hosting", deps)

    def test_parse_nuspec_xml(self) -> None:
        """Test extracting dependencies from nuspec XML string."""
        xml_content = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<package xmlns="http://schemas.microsoft.com/packaging/'
            '2013/05/nuspec.xsd">\n'
            '  <metadata>\n'
            '    <id>SamplePackage</id>\n'
            '    <version>1.0.0</version>\n'
            '    <dependencies>\n'
            '      <group targetFramework="net8.0">\n'
            '        <dependency id="DepA" version="1.0.0" />\n'
            '        <dependency id="DepB" version="2.0.0" />\n'
            '      </group>\n'
            '    </dependencies>\n'
            '  </metadata>\n'
            '</package>'
        )
        deps = parse_nuspec_content(xml_content)
        self.assertEqual(deps, ["DepA", "DepB"])

    def test_parse_test_repo_json(self) -> None:
        """Test parsing test repository in JSON format."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json", encoding="utf-8"
        ) as file_handle:
            file_handle.write('{"A": ["B", "C"], "B": ["D"], "C": []}')
            temp_name = file_handle.name

        graph = parse_test_repo_file(temp_name)
        self.assertEqual(graph.get("A"), ["B", "C"])
        self.assertEqual(graph.get("B"), ["D"])
        self.assertEqual(graph.get("C"), [])

    def test_parse_test_repo_text(self) -> None:
        """Test parsing test repository in text format."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt", encoding="utf-8"
        ) as file_handle:
            file_handle.write("A -> B, C\nB -> D\nC:\n")
            temp_name = file_handle.name

        graph = parse_test_repo_file(temp_name)
        self.assertEqual(graph.get("A"), ["B", "C"])
        self.assertEqual(graph.get("B"), ["D"])
        self.assertEqual(graph.get("C"), [])

    def test_get_direct_dependencies_test_mode(self) -> None:
        """Test getting direct dependencies in test repository mode."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json", encoding="utf-8"
        ) as file_handle:
            file_handle.write('{"X": ["Y", "Z"]}')
            temp_name = file_handle.name

        deps = get_direct_dependencies("X", temp_name, test_mode=True)
        self.assertEqual(deps, ["Y", "Z"])

    @patch("src.collector.fetch_json")
    def test_fetch_nuget_dependencies_mocked(
        self, mock_fetch_json: MagicMock
    ) -> None:
        """Test fetching NuGet direct dependencies with mocked API response."""
        mock_fetch_json.return_value = {
            "items": [
                {
                    "items": [
                        {
                            "catalogEntry": {
                                "dependencyGroups": [
                                    {
                                        "dependencies": [
                                            {"id": "Alpha"},
                                            {"id": "Beta"},
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        deps = fetch_nuget_dependencies(
            "https://api.nuget.org/v3/registration5-semver1", "SamplePkg"
        )
        self.assertEqual(deps, ["Alpha", "Beta"])


if __name__ == "__main__":
    unittest.main()
