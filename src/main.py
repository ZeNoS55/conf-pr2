"""Main entry point for stage 2: direct dependencies display."""

import sys
from typing import List, Optional
from src.cli import parse_arguments
from src.collector import get_direct_dependencies

EMPTY_COUNT = 0


def main(argv: Optional[List[str]] = None) -> int:
    """Retrieve and display direct dependencies of package."""
    cfg = parse_arguments(argv)
    deps = get_direct_dependencies(
        cfg.package_name, cfg.repo, test_mode=cfg.test_mode
    )
    print(f"=== Stage 2: Direct Dependencies for {cfg.package_name} ===")
    if len(deps) == EMPTY_COUNT:
        print("(No direct dependencies found)")
    else:
        for dep in deps:
            print(f"- {dep}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
