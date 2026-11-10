"""Main entry point for stage 1: CLI configuration display."""

import sys
from typing import List, Optional
from src.cli import parse_arguments
from src.config import format_config_kv


def main(argv: Optional[List[str]] = None) -> int:
    """Parse CLI options and output parameters in key-value format."""
    cfg = parse_arguments(argv)
    print("=== Stage 1: Configuration ===")
    print(format_config_kv(cfg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
