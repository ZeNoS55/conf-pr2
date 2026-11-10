"""Command-line interface argument parsing module."""

import argparse
from typing import List, Optional
from src.config import (
    Config,
    DEFAULT_MAX_DEPTH,
    DEFAULT_REPO_URL,
    validate_config,
)

STAGE_MIN = 1
STAGE_MAX = 5


def add_core_arguments(parser: argparse.ArgumentParser) -> None:
    """Register core required and main path parameters."""
    parser.add_argument(
        "-p",
        "--package",
        dest="package_name",
        required=True,
        help="Name of package to analyze.",
    )
    parser.add_argument(
        "-r",
        "--repo",
        dest="repo",
        default=DEFAULT_REPO_URL,
        help="Repository URL or path to test repository file.",
    )
    parser.add_argument(
        "-t",
        "--test-mode",
        dest="test_mode",
        action="store_true",
        help="Enable test repository mode.",
    )


def add_optional_arguments(parser: argparse.ArgumentParser) -> None:
    """Register optional filter, depth and display parameters."""
    parser.add_argument(
        "-d",
        "--max-depth",
        dest="max_depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help="Maximum depth of dependency analysis.",
    )
    parser.add_argument(
        "-f",
        "--filter",
        dest="filter_substring",
        default="",
        help="Substring for package filtering.",
    )
    parser.add_argument(
        "-s",
        "--stage",
        dest="stage",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Target stage to execute (1-5).",
    )
    parser.add_argument(
        "--no-gui",
        dest="no_gui",
        action="store_true",
        help="Disable automatic graphical display window.",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="dep-visualizer",
        description="Dependency graph visualizer for .NET NuGet packages.",
    )
    add_core_arguments(parser)
    add_optional_arguments(parser)
    return parser


def parse_arguments(args: Optional[List[str]] = None) -> Config:
    """Parse and validate command-line arguments."""
    parser = create_parser()
    parsed = parser.parse_args(args)
    cfg = Config(
        package_name=parsed.package_name,
        repo=parsed.repo,
        test_mode=parsed.test_mode,
        max_depth=parsed.max_depth,
        filter_substring=parsed.filter_substring,
        stage=parsed.stage,
    )
    validate_config(cfg)
    return cfg
