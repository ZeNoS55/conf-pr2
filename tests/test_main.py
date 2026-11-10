"""Integration tests for main CLI dispatcher."""

import unittest
from unittest.mock import MagicMock, patch
from src.main import main

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class TestMainCli(unittest.TestCase):
    """Test suite for top-level CLI main function."""

    def test_main_stage1(self) -> None:
        """Test invoking main for Stage 1."""
        code = main(
            [
                "--package",
                "A",
                "--repo",
                "test_repos/diamond.json",
                "--test-mode",
                "--stage",
                "1",
            ]
        )
        self.assertEqual(code, EXIT_SUCCESS)

    def test_main_stage2(self) -> None:
        """Test invoking main for Stage 2."""
        code = main(
            [
                "--package",
                "A",
                "--repo",
                "test_repos/diamond.json",
                "--test-mode",
                "--stage",
                "2",
            ]
        )
        self.assertEqual(code, EXIT_SUCCESS)

    def test_main_stage3(self) -> None:
        """Test invoking main for Stage 3."""
        code = main(
            [
                "--package",
                "A",
                "--repo",
                "test_repos/diamond.json",
                "--test-mode",
                "--stage",
                "3",
            ]
        )
        self.assertEqual(code, EXIT_SUCCESS)

    def test_main_stage4(self) -> None:
        """Test invoking main for Stage 4."""
        code = main(
            [
                "--package",
                "A",
                "--repo",
                "test_repos/diamond.json",
                "--test-mode",
                "--stage",
                "4",
            ]
        )
        self.assertEqual(code, EXIT_SUCCESS)

    @patch("src.main.render_plantuml_to_png")
    def test_main_stage5(self, mock_render: MagicMock) -> None:
        """Test invoking main for Stage 5."""
        mock_render.return_value = False
        code = main(
            [
                "--package",
                "A",
                "--repo",
                "test_repos/diamond.json",
                "--test-mode",
                "--stage",
                "5",
                "--no-gui",
            ]
        )
        self.assertEqual(code, EXIT_SUCCESS)

    def test_main_validation_error(self) -> None:
        """Test that invalid config causes main to return error code."""
        code = main(
            [
                "--package",
                "A",
                "--repo",
                "test_repos/diamond.json",
                "--test-mode",
                "--max-depth",
                "-2",
            ]
        )
        self.assertEqual(code, EXIT_FAILURE)


if __name__ == "__main__":
    unittest.main()
