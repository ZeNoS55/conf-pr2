"""Configuration and CLI parameter validation module."""

import os
from dataclasses import dataclass
from typing import Optional

ZERO = 0
EMPTY_LEN = 0
DEFAULT_MAX_DEPTH = 5
DEFAULT_REPO_URL = "https://api.nuget.org/v3/registration5-semver1"
HTTP_PREFIX = "http://"
HTTPS_PREFIX = "https://"


@dataclass
class Config:
    """Application configuration settings."""

    package_name: str
    repo: str
    test_mode: bool
    max_depth: int
    filter_substring: str
    stage: Optional[int] = None
    no_gui: bool = False


def validate_package_name(name: str, test_mode: bool) -> None:
    """Validate package name parameter."""
    if len(name.strip()) == EMPTY_LEN:
        raise ValueError("Package name cannot be empty.")
    if test_mode:
        if not name.isupper() or not name.isalpha():
            raise ValueError(
                "Test package name must consist of uppercase Latin letters."
            )


def validate_repo(repo: str, test_mode: bool) -> None:
    """Validate repository URL or file path parameter."""
    stripped_repo = repo.strip()
    if len(stripped_repo) == EMPTY_LEN:
        raise ValueError("Repository cannot be empty.")
    if test_mode:
        if not os.path.isfile(stripped_repo):
            raise ValueError(
                f"Test repository file not found: {stripped_repo}"
            )
    else:
        is_http = stripped_repo.startswith(HTTP_PREFIX)
        is_https = stripped_repo.startswith(HTTPS_PREFIX)
        if not (is_http or is_https):
            raise ValueError(
                "Repository URL must start with http:// or https://."
            )


def validate_max_depth(depth: int) -> None:
    """Validate maximum recursion depth parameter."""
    if depth < ZERO:
        raise ValueError(
            "Maximum depth must be a non-negative integer (>= 0)."
        )


def validate_config(cfg: Config) -> None:
    """Validate all configuration fields."""
    validate_package_name(cfg.package_name, cfg.test_mode)
    validate_repo(cfg.repo, cfg.test_mode)
    validate_max_depth(cfg.max_depth)


def format_config_kv(cfg: Config) -> str:
    """Format configuration parameters as key-value pairs."""
    lines = [
        f"package_name: {cfg.package_name}",
        f"repo: {cfg.repo}",
        f"test_mode: {cfg.test_mode}",
        f"max_depth: {cfg.max_depth}",
        f"filter_substring: {cfg.filter_substring}",
    ]
    return "\n".join(lines)
