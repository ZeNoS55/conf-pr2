"""Unit tests for Stage 1: CLI and configuration validation."""

import os
import tempfile
import unittest
from src.cli import parse_arguments
from src.config import Config, format_config_kv, validate_config

NEGATIVE_DEPTH = -1
VALID_DEPTH = 3
SAMPLE_DEPTH = 4


class TestStage1Configuration(unittest.TestCase):
    """Test suite for configuration parsing and validation."""

    def setUp(self) -> None:
        """Create temporary test file for repository checks."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        )
        self.temp_file.write("{}")
        self.temp_file.close()

    def tearDown(self) -> None:
        """Remove temporary test file."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_valid_cli_arguments(self) -> None:
        """Test parsing valid CLI parameters in normal mode."""
        args = [
            "--package",
            "Serilog.AspNetCore",
            "--max-depth",
            str(VALID_DEPTH),
            "--filter",
            "Microsoft",
        ]
        cfg = parse_arguments(args)
        self.assertEqual(cfg.package_name, "Serilog.AspNetCore")
        self.assertEqual(cfg.max_depth, VALID_DEPTH)
        self.assertEqual(cfg.filter_substring, "Microsoft")
        self.assertFalse(cfg.test_mode)

    def test_valid_test_mode_arguments(self) -> None:
        """Test parsing valid CLI parameters in test mode."""
        args = [
            "--package",
            "A",
            "--repo",
            self.temp_file.name,
            "--test-mode",
            "--max-depth",
            str(SAMPLE_DEPTH),
        ]
        cfg = parse_arguments(args)
        self.assertEqual(cfg.package_name, "A")
        self.assertTrue(cfg.test_mode)
        self.assertEqual(cfg.repo, self.temp_file.name)

    def test_empty_package_name_raises(self) -> None:
        """Test validation failure for empty package name."""
        cfg = Config(
            package_name="   ",
            repo="https://api.nuget.org/v3",
            test_mode=False,
            max_depth=VALID_DEPTH,
            filter_substring="",
        )
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_invalid_test_package_name_raises(self) -> None:
        """Test validation failure for lowercase package in test mode."""
        cfg = Config(
            package_name="pkg123",
            repo=self.temp_file.name,
            test_mode=True,
            max_depth=VALID_DEPTH,
            filter_substring="",
        )
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_invalid_repo_url_raises(self) -> None:
        """Test validation failure for repository URL without HTTP schema."""
        cfg = Config(
            package_name="Serilog",
            repo="ftp://invalid.url",
            test_mode=False,
            max_depth=VALID_DEPTH,
            filter_substring="",
        )
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_missing_test_repo_file_raises(self) -> None:
        """Test validation failure when test repo file is missing."""
        cfg = Config(
            package_name="A",
            repo="non_existent_file_12345.json",
            test_mode=True,
            max_depth=VALID_DEPTH,
            filter_substring="",
        )
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_negative_max_depth_raises(self) -> None:
        """Test validation failure for negative max depth."""
        cfg = Config(
            package_name="Serilog",
            repo="https://api.nuget.org/v3",
            test_mode=False,
            max_depth=NEGATIVE_DEPTH,
            filter_substring="",
        )
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_format_config_kv(self) -> None:
        """Test key-value formatting string."""
        cfg = Config(
            package_name="Newtonsoft.Json",
            repo="https://api.nuget.org/v3",
            test_mode=False,
            max_depth=VALID_DEPTH,
            filter_substring="Bcl",
        )
        kv_output = format_config_kv(cfg)
        self.assertIn("package_name: Newtonsoft.Json", kv_output)
        self.assertIn("max_depth: 3", kv_output)
        self.assertIn("filter_substring: Bcl", kv_output)


if __name__ == "__main__":
    unittest.main()
